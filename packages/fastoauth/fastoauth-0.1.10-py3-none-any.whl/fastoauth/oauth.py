# -*- coding: utf-8 -*-
"""
@author: hubo
@project: bb_fast_oauth2
@file: oauth.py
@time: 2023/11/01
@desc: 对oauth2中一些基本操作的封装
"""
import copy

import json
import time
from calendar import timegm
from contextvars import ContextVar
from datetime import datetime, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, status, Request
from starlette.responses import JSONResponse
import secrets
import uuid
import re

from starlette.middleware.base import BaseHTTPMiddleware

from .schemas import Token
from ._redis import _Redis

current_user: ContextVar = ContextVar("current_user", default=None)


def get_current_user():
    return current_user.get()


class OAuth2:
    SECRET_KEY = secrets.token_bytes(32).hex()  # SECRET_KEY进行加密用的key
    EXPIRE_SECONDS = 60*60*2    # token有效期，单位秒。默认两个小时
    REDIS_URL = None            # 指定redis，格式redis://user:password@localhost:6379/db
    ALGORITHM = "HS256"         # 加密Token的算法

    @staticmethod
    def create_access_token(data: dict, expire_seconds=None):
        to_encode = data.copy()
        # 使用时区感知的UTC时间，避免对 utcnow 的警告
        expire = int(datetime.now(timezone.utc).timestamp())
        if not expire_seconds:
            expire_seconds = OAuth2.EXPIRE_SECONDS
        expire += expire_seconds
        to_encode.update({"exp": expire})
        access_token, refresh_token = OAuth2._encode(to_encode)
        # to_encode.update({"_refresh": True})
        # refresh_token = OAuth2._encode(to_encode)
        # 暂不使用refresh_token，直接使用access_token进行刷新。一般refresh_token的有效期是access_token有效期的2倍
        return Token(access_token=access_token, refresh_token=refresh_token, token_type='bearer', expires_in=expire_seconds)

    @staticmethod
    def refresh_token(token, expire_seconds=None):
        payload = OAuth2._decode(token)
        if "_refresh" not in payload:
            # 只有refresh_token才可以刷新token
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a refresh token")
        # 删除refresh项
        del payload["_refresh"]
        return OAuth2.create_access_token(payload, expire_seconds)

    @staticmethod
    def remove_token(token):
        """如果启用redis，后端支持logout"""
        if _Redis().enabled_from(OAuth2.REDIS_URL):
            data = OAuth2._decode(token)
            # 配置redis，删除token
            _Redis().delete(token)
            _Redis().delete(data["refresh_token"])

    @staticmethod
    def get_token_user(token):
        """得到token中的数据"""
        data = OAuth2._decode(token)
        if "_refresh" in data:
            # refresh_token
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a access token")
        return data

    @staticmethod
    def _encode(data):
        token_data = copy.copy(data)
        exp = data['exp']
        refresh_exp = max(exp, int(datetime.now(timezone.utc).timestamp())+(60*60*24*30))  # refresh_token的有效期最短是30天
        """如果未启用redis，将整个数据加密作为token；如果启用了redis，把数据存在redis，并返回一个相对简短的加密的key作为token"""
        if _Redis().enabled_from(OAuth2.REDIS_URL):
            # 启用了redis，只加密一个唯一键作为检索的依据
            token = jwt.encode({'uid': str(uuid.uuid1())}, secrets.token_bytes(32).hex(), algorithm=OAuth2.ALGORITHM)
            refresh_token = jwt.encode({'uid': str(uuid.uuid1())}, secrets.token_bytes(32).hex(), algorithm=OAuth2.ALGORITHM)
            token_data["refresh_token"] = refresh_token
            _Redis().set(token, json.dumps(token_data), expire_in=exp)
            token_data.update({"_refresh": True})
            token_data.update({"exp": refresh_exp})
            # refresh_token的有效期最短是30天
            _Redis().set(refresh_token, json.dumps(token_data), expire_in=refresh_exp)
            return token, refresh_token
        else:
            # 未启用redis，将整个token_data加密，将加密后的字符串作为access_token
            token = jwt.encode(token_data, OAuth2.SECRET_KEY, algorithm=OAuth2.ALGORITHM)
            token_data.update({"_refresh": True})
            token_data.update({"exp": refresh_exp})
            refresh_token = jwt.encode(token_data, OAuth2.SECRET_KEY, algorithm=OAuth2.ALGORITHM)
            return token, refresh_token

    @staticmethod
    def _decode(token):
        """如果未启用redis，token解密后就是完整数据；如果启用了redis，token只是redis的一个key，从redis取回完整数据"""
        if _Redis().enabled_from(OAuth2.REDIS_URL):
            # 启用了redis，token只是Redis里的检索依据
            data = _Redis().get(token)
            if not data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return json.loads(data)
        else:
            # 未启用redis，将整个token解密，得到原始数据
            try:
                return jwt.decode(token, OAuth2.SECRET_KEY, algorithms=[OAuth2.ALGORITHM])
            except JWTError:
                raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Could not validate credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                    )


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        authorization_header = request.headers.get('Authorization')
        if authorization_header:
            try:
                token = authorization_header.split(" ")[1]
                current_user.set(OAuth2.get_token_user(token))
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, headers={"WWW-Authenticate": "Bearer"},
                                    content={"detail": e.detail})
        response = await call_next(request)
        return response

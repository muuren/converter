from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import TypeVar

import jwt
from passlib.hash import argon2

from app.auth.config import JWTConfig


class BaseToken(ABC):
    def __init__(self, config: JWTConfig, typ: str):
        self.type = typ
        self.config = config

    @abstractmethod
    def create_token(self, user_data: dict) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str | bytes):
        pass


TokenProvider = TypeVar("TokenProvider", bound=BaseToken)


class JWTToken(BaseToken):
    def __init__(self, config: JWTConfig, typ: str = "bearer"):
        super().__init__(config, typ)

    def create_token(self, user_data: dict) -> str:
        """Generates JWT token with registered claim names: "exp", "iat", "iss".

        Args:
            user_data (dict): user data to add to a payload
        """
        expire = datetime.utcnow() + timedelta(minutes=self.config.expire_min)

        payload = dict(exp=expire, iat=datetime.utcnow(), iss=self.config.issuer)
        payload.update(**user_data)
        return jwt.encode(
            payload=payload, key=self.config.key, algorithm=self.config.algorithm
        )

    def verify_token(self, token: str | bytes):
        return jwt.decode(
            jwt=token,
            key=self.config.key,
            algorithms=[self.config.algorithm],
            issuer=self.config.issuer,
        )


class BaseAuth(ABC):
    @classmethod
    @abstractmethod
    def verify_password(cls, plain_secret: str, hashed_value: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def hash_password(cls, plain_secret: str) -> str:
        pass


AuthProvider = TypeVar("AuthProvider", bound=BaseAuth)


class Argon2Auth(BaseAuth):
    @classmethod
    def verify_password(cls, plain_secret: str, hashed_value: str) -> bool:
        try:
            return argon2.verify(
                secret=plain_secret, hash=hashed_value
            )
        except ValueError:
            return False

    @classmethod
    def hash_password(cls, plain_secret: str) -> str:
        """Hash secret string with auto-generated salt."""
        return argon2.hash(plain_secret)

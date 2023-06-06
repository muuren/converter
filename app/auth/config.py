import os
from typing import NamedTuple


class PostgresConfig(NamedTuple):
    user: str = os.getenv("POSTGRES_USERNAME", default="local_user")
    password: str = os.getenv("POSTGRES_PASSWORD", default="localpassword")
    host: str = os.getenv("POSTGRES_HOST", default="localhost")
    port: str = os.getenv("POSTGRES_PORT", default="32769")
    database: str = os.getenv("POSTGRES_DATABASE", default="localdb")
    schema: str = os.getenv("POSTGRES_SCHEMA", default="app")
    driver: str = os.getenv("POSTGRES_DRIVER", default="postgresql+asyncpg")
    app_name: str = os.getenv("POSTGRES_APP_NAME", default="app")

    @property
    def url(self):
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def __str__(self):
        excluded_attr = ("count", "index", "url", "password")
        attrs = [
            f"{attr}={getattr(self, attr)}"
            for attr in dir(self)
            if not attr.startswith("_") and attr not in excluded_attr
        ]
        return f"PostgresConfig({', '.join(attrs)})"


class JWTConfig(NamedTuple):
    algorithm: str = os.getenv("JWT_ALGORITHM", default="HS256")
    key: str = os.getenv("JWT_KEY", default="development_key")
    issuer: str = os.getenv("JWT_ISSUER", default="IdentityServer")
    expire_min: int = int(os.getenv("JWT_EXPIRE_MIN", default=60))

    def __str__(self):
        return f"JWTConfig(algorithm={self.algorithm}, issuer={self.issuer}, expire_min={self.expire_min})"

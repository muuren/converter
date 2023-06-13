import os
from typing import NamedTuple, Optional


class PostgresConfig(NamedTuple):
    user: Optional[str] = os.getenv("POSTGRES_USERNAME")
    password: Optional[str] = os.getenv("POSTGRES_PASSWORD")
    host: Optional[str] = os.getenv("POSTGRES_HOST")
    port: Optional[str] = os.getenv("POSTGRES_PORT", default="32768")
    database: Optional[str] = os.getenv("POSTGRES_DATABASE")
    schema: Optional[str] = os.getenv("POSTGRES_SCHEMA")
    driver: Optional[str] = "postgresql+asyncpg"
    app_name: Optional[str] = os.getenv("POSTGRES_APP_NAME")
    timeout: Optional[int] = int(os.getenv("POSTGRES_TIMEOUT", default=3))

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
    key: Optional[str] = os.getenv("JWT_KEY")
    issuer: Optional[str] = os.getenv("JWT_ISSUER")
    expire_min: Optional[int] = int(os.getenv("JWT_EXPIRE_MIN", default=60))

    def __str__(self):
        return f"JWTConfig(algorithm={self.algorithm}, issuer={self.issuer}, expire_min={self.expire_min})"


pg_config = PostgresConfig()
jwt_config = JWTConfig()

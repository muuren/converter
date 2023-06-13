import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import registry, relationship

from app.auth.config import pg_config
from app.auth.models import User, PWDHash

metadata = sa.MetaData(schema=pg_config.schema)

users_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("email", sa.String(40), unique=True, index=True),
)

pwdhashes_table = sa.Table(
    "pwdhashes",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "user_id",
        sa.Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    ),
    sa.Column("value", sa.String(), nullable=False),
)


def register_mapping():
    mapper_registry = registry()
    user_mapper = mapper_registry.map_imperatively(User, users_table)
    mapper_registry.map_imperatively(
        PWDHash, pwdhashes_table, properties={"users": relationship(user_mapper)}
    )

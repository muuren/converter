from app.auth import models as m
from app.auth.dao import AuthDao
from app.auth.schema import UserCredentials
from app.auth.security import AuthProvider, TokenProvider


class InvalidCredentials(BaseException):
    pass


class UserAlreadyExists(BaseException):
    pass


async def login_handler(
        cred: UserCredentials,
        dao: AuthDao,
        auth: AuthProvider,
        token: TokenProvider,
):
    user_id = await dao.get_user_id(cred.email)
    if not user_id:
        raise InvalidCredentials

    hash_value = await dao.get_pwdhash_value(user_id)
    if not auth.verify_password(cred.password, hash_value):
        raise InvalidCredentials

    return {
        "access_token": token.create_token({"email": cred.email}),
        "token_type": token.type,
    }


async def sign_up_handler(
        cred: UserCredentials,
        dao: AuthDao,
        auth: AuthProvider,
):
    user_id = await dao.get_user_id(cred.email)
    if user_id:
        raise UserAlreadyExists

    new_user = m.User(email=cred.email)
    password_hash = m.PWDHash(value=auth.hash_password(cred.password))
    password_hash.users = new_user  # type: ignore
    await dao.add_one(password_hash)
    return new_user

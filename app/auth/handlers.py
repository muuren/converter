from sqlalchemy.exc import IntegrityError, DBAPIError

from app.auth import models as m
from app.auth.dao import AuthDao
from app.auth.schema import UserCredentials
from app.auth.security import AuthProvider, TokenProvider
from app.utils import Retry


class InvalidCredentials(BaseException):
    pass


class UserAlreadyExists(BaseException):
    pass


@Retry(attempts=3, delay=1.5)
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

no_retry_on_error = (DBAPIError, IntegrityError)


@Retry(attempts=3, delay=1.5, exclude_exc=no_retry_on_error)
async def sign_up_handler(
    cred: UserCredentials,
    dao: AuthDao,
    auth: AuthProvider,
) -> m.User:
    user_id = await dao.get_user_id(cred.email)
    if user_id:
        raise UserAlreadyExists

    new_user = m.User(email=cred.email)
    password_hash = m.PWDHash(value=auth.hash_password(cred.password))
    password_hash.users = new_user  # type: ignore
    try:
        await dao.add_one(password_hash)
        return new_user
    except IntegrityError:
        raise UserAlreadyExists

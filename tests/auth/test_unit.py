import datetime

import jwt
import pytest
import time
from pydantic import ValidationError

from app.auth import handlers as h
from app.auth.config import JWTConfig
from app.auth.models import User
from app.auth.schema import UserCredentials
from app.auth.security import JWTToken


def test_empty_email_credentials_raises_error():
    with pytest.raises(ValidationError):
        UserCredentials(email="", password="123456789")


class TestJWT:

    def test_jwt_token_create_token(self, auth_tokenizer, username="user"):
        token = auth_tokenizer.create_token({"username": username})
        token_parts = len(str(token).split("."))
        assert token
        assert token_parts == 3

    def test_jwt_token_bad_issuer_raise_error(self, auth_tokenizer, username="user"):
        tokenizer = JWTToken(JWTConfig(issuer="fake_issuer"))
        user_token = tokenizer.create_token({"username": username})

        with pytest.raises(jwt.InvalidIssuerError):
            auth_tokenizer.verify_token(user_token)

    def test_expired_jwt_token_raise_error(self, auth_tokenizer, username="user"):
        expire = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        payload = {"username": username, "exp": expire}
        expired_token = auth_tokenizer.create_token(payload)
        with pytest.raises(jwt.ExpiredSignatureError):
            auth_tokenizer.verify_token(expired_token)

    def test_malformed_jwt_token_raise_error(self, auth_tokenizer):
        token = "dlkfjal;kdfjsl;kfjdlkfjsdf"
        with pytest.raises(jwt.DecodeError):
            auth_tokenizer.verify_token(token)


def test_argon_auth_return_hash(test_auth):
    start_time = time.time()
    test_string = "some_p@ssw0rd"
    data_hash = test_auth.hash_password(test_string)
    end_time = time.time() - start_time
    assert end_time < 0.04
    assert data_hash.startswith("$argon2id$v=")


def test_argon_auth_validate_hash(test_auth):
    test_string = "some_p@ssw0rd"
    data_hash = test_auth.hash_password(test_string)

    assert test_auth.verify_password(test_string, data_hash)


@pytest.mark.asyncio
async def test_login_registered_user_return_token(
        user_form_data, fake_dao, test_auth, auth_tokenizer
):
    token = await h.login_handler(user_form_data, fake_dao, test_auth, auth_tokenizer)

    assert token["access_token"]
    assert token["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_new_user_raises_error(
        new_user_form_data, fake_dao, test_auth, auth_tokenizer
):
    with pytest.raises(h.InvalidCredentials):
        await h.login_handler(new_user_form_data, fake_dao, test_auth, auth_tokenizer)


@pytest.mark.asyncio
async def test_sign_up_new_user_return_user_model(
        new_user_form_data, fake_dao, test_auth
):
    user = await h.sign_up_handler(new_user_form_data, fake_dao, test_auth)

    assert isinstance(user, User)
    assert user.email == new_user_form_data.email


@pytest.mark.asyncio
async def test_sign_up_registered_user_raises_error(
        user_form_data, fake_dao, test_auth, auth_tokenizer
):
    with pytest.raises(h.UserAlreadyExists):
        await h.sign_up_handler(user_form_data, fake_dao, test_auth)

from fastapi import Form
from pydantic import BaseModel, EmailStr, constr, SecretStr


class UserCredentials(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=20)  # type: ignore

    def __str__(self):
        return f"UserCredentials(email='{self.email}')"


class PasswordRequestForm:
    """
    It creates the following Form request parameters in your endpoint:

    email: email string. The OAuth2 spec requires the exact field name "username".
    password: password string. The OAuth2 spec requires the exact field name "password".
    """

    def __init__(
        self,
        email: str = Form(default="name@email.com"),
        password: str = Form(min_length=6, max_length=20),
    ):
        self.email = email
        self.password = SecretStr(password)

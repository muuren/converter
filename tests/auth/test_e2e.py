import pytest
from fastapi import status

from app.auth.schema import UserCredentials

sign_up_endpoint = "/api/sign_up"
login_endpoint = "/api/login"

new_user_form_data = UserCredentials(email="abc@mail.post", password="-123456789")


@pytest.mark.usefixtures("test_tables_teardown")
def test_hostname_route(test_app):
    response = test_app.get("/")
    assert response.status_code == 200


@pytest.mark.usefixtures("test_tables_teardown")
def test_register_new_user_return_status_201(test_app):
    result = test_app.post(sign_up_endpoint, data=new_user_form_data.json())
    assert result.status_code == status.HTTP_201_CREATED


@pytest.mark.usefixtures("test_tables_teardown")
def test_register_existing_user_return_status_422(test_app):
    user_created = test_app.post(sign_up_endpoint, data=new_user_form_data.json())
    assert user_created.status_code == status.HTTP_201_CREATED

    result = test_app.post(sign_up_endpoint, data=new_user_form_data.json())
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert result.json()["detail"] == "User already exists"


@pytest.mark.usefixtures("test_tables_teardown")
def test_login_new_user_return_status_401(test_app):
    result = test_app.post(login_endpoint, data=new_user_form_data.json())
    assert result.status_code == status.HTTP_401_UNAUTHORIZED

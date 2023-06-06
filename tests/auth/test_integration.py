import pytest

from app.auth.dao import AuthDao
from app.auth.models import User, PWDHash

pytestmark = pytest.mark.usefixtures("mappers")


@pytest.mark.asyncio
async def test_auth_dao_get_user_id_by_email(auth_dao: AuthDao):
    user = User(email="test668@email.com")
    registered_id = await auth_dao.add_one(user)

    queried_id = await auth_dao.get_user_id(user.email)
    assert queried_id == registered_id


@pytest.mark.asyncio
async def test_auth_dao_add_one(auth_dao: AuthDao):
    data_hash1 = PWDHash(value="123456789", user_id=15)
    data_hash2 = PWDHash(value="133133133", user_id=1000)
    data_id1 = await auth_dao.add_one(data_hash1)
    data_id2 = await auth_dao.add_one(data_hash2)
    assert (data_id1, data_id2) == (1, 2)


@pytest.mark.asyncio
async def test_auth_dao_get_pwdhash_by_user_id(auth_dao: AuthDao):
    data_hash1 = PWDHash(value="123456789", user_id=15)
    data_hash2 = PWDHash(value="133133133", user_id=1000)
    await auth_dao.add_all([data_hash1, data_hash2])

    result1 = await auth_dao.get_pwdhash_value(user_id=15)
    result2 = await auth_dao.get_pwdhash_value(user_id=1000)
    assert (result1, result2) == ("123456789", "133133133")

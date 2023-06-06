from fastapi import APIRouter, HTTPException, status, Depends

from app.auth import dependencies as deps
from app.auth import handlers
from app.auth.schema import UserCredentials

auth_router = APIRouter(tags=["authentication"], prefix="/api/v1")


@auth_router.post("/login/")
async def login(
        form_data: UserCredentials,
        dao=Depends(deps.get_dao_provider),
        auth=Depends(deps.get_auth_provider),
        token=Depends(deps.get_token_provider),
):
    """Login endpoint."""

    try:
        return await handlers.login_handler(form_data, dao, auth, token)
    except handlers.InvalidCredentials:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


@auth_router.post("/sign_up/", status_code=status.HTTP_201_CREATED)
async def sign_up(
        form_data: UserCredentials,
        dao=Depends(deps.get_dao_provider),
        auth=Depends(deps.get_auth_provider),
):
    """New user registration endpoint."""

    try:
        return await handlers.sign_up_handler(form_data, dao, auth)
    except handlers.UserAlreadyExists:
        raise HTTPException(status_code=422, detail="User already exists")

from fastapi import APIRouter, HTTPException, status

from ..models import LoginIn, LoginOut
from ..security import current_user, issue_token, verify_passcode
from ..state import get_pair, partner_of
from fastapi import Depends

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/login", response_model=LoginOut)
async def login(body: LoginIn) -> LoginOut:
    if not verify_passcode(body.name, body.passcode):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong name or passcode")
    return LoginOut(token=issue_token(body.name), name=body.name)


@router.get("/me")
async def me(user: str = Depends(current_user)) -> dict:
    pair = await get_pair()
    return {
        "name": user,
        "partner": await partner_of(user),
        "members": pair.get("members") or [],
        "exam_date": pair.get("exam_date"),
    }

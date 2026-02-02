from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from .utils import decode_token
from typing import List

pswd = OAuth2PasswordBearer(tokenUrl='/login')

def get_current_user(token: str=Depends(pswd)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401,detail="Could not validate credentials.")
    return payload

def require_rank(allowed_ranks: List[str]):
    def rank_checker(current_user: dict = Depends(get_current_user)):
        user_rank = current_user.get("rank")
        if user_rank not in allowed_ranks:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action not permitted for rank: {user_rank}"
            )
        return current_user
    return rank_checker
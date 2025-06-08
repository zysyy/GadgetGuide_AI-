# backend/auth/deps.py
from fastapi import Depends, HTTPException, status
from backend.auth.routes import get_current_user

def require_admin(current_user = Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅限管理员访问")
    return current_user

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_user
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.user import UserOut
from app.security import authenticate_user, get_password_hash

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["user"] = user.username
    return user


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"detail": "Logged out"}


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if len(payload.password) > 72:
        raise HTTPException(status_code=400, detail="Password must be at most 72 characters long")
    user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(require_user)):
    return user

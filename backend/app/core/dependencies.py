"""FastAPI dependencies."""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User


def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Stub for getting current user.
    For MVP, returns a fake user with id=1.
    TODO: Replace with real authentication middleware.
    """
    # Try to get or create user with id=1
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        user = User(id=1, email="user@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def create_user(
    db: Session, *, email: str, hashed_password: str, full_name: str, role: str
) -> User:
    user = User(
        email=email.lower(),
        hashed_password=hashed_password,
        full_name=full_name.strip(),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

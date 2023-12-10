from sqlalchemy import select
from sqlalchemy.orm import Session

from models import User


class CRUDUser:
    def __init__(self, model):
        self.model = model

    def get(self, db: Session, id: int) -> User | None:
        return db.execute(select(User).filter_by(id=id)).scalars().first()

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.execute(select(User).filter_by(email=email)).scalars().first()

    def create(self, db: Session, email: str, first_name: str, last_name: str) -> User:
        new_user = User(email=email, first_name=first_name, last_name=last_name)
        db.add(new_user)
        return new_user


user = CRUDUser(User)

"""Model for Costos Construccion"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from .. import database
from ..middlewares.database import Template


class UserModel(database.BASE):
    """Model for Users"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), default="member", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), nullable=False)
    deleted_at = Column(DateTime)

    activity_logs = relationship("ActivityLogModel", back_populates="user")
    invitations = relationship("InvitationModel", back_populates="user")
    team_members = relationship("TeamMemberModel", back_populates="user")

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)


class UserBase(BaseModel):
    name: Optional[constr(max_length=100)]
    email: EmailStr
    role: Optional[constr(max_length=20)] = "member"


class UserCreate(UserBase):
    password_hash: str


class UserSchema(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True


class Users(Template):
    def __init__(self, db, Schema: str = "SCHEMA") -> None:
        schemas = {
            "BASE": UserBase,
            "CREATE": UserCreate,
            "SCHEMA": UserSchema,
        }
        super().__init__(Model=UserModel, db=db, Schema=schemas.get(Schema, UserSchema))

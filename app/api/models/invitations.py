"""Model for Invitation"""

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


class InvitationModel(database.BASE):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(
        Integer,
        ForeignKey("teams.id", ondelete="NO ACTION", onupdate="NO ACTION"),
        nullable=False,
    )
    email = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    invited_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="NO ACTION", onupdate="NO ACTION"),
        nullable=False,
    )
    invited_at = Column(DateTime, default=func.now(), nullable=False)
    status = Column(String(20), default="pending", nullable=False)

    team = relationship("TeamModel", back_populates="invitations")
    user = relationship("UserModel", back_populates="invitations")


class InvitationBase(BaseModel):
    team_id: int
    email: EmailStr
    role: constr(max_length=50)
    invited_by: int
    status: Optional[constr(max_length=20)] = "pending"


class InvitationCreate(InvitationBase):
    pass


class Invitation(InvitationBase):
    id: int
    invited_at: datetime

    class Config:
        orm_mode = True


class Invitations(Template):
    def __init__(self, db, Schema: str = "SCHEMA") -> None:
        schemas = {
            "SCHEMA": Invitation,
            "BASE": InvitationBase,
            "CREATE": InvitationCreate,
        }
        super().__init__(
            Model=InvitationModel, db=db, Schema=schemas.get(Schema, Invitation)
        )

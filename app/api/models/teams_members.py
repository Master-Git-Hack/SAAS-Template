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


class TeamMemberModel(database.BASE):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="NO ACTION", onupdate="NO ACTION"),
        nullable=False,
    )
    team_id = Column(
        Integer,
        ForeignKey("teams.id", ondelete="NO ACTION", onupdate="NO ACTION"),
        nullable=False,
    )
    role = Column(String(50), nullable=False)
    joined_at = Column(DateTime, default=func.now(), nullable=False)

    team = relationship("TeamModel", back_populates="team_members")
    user = relationship("UserModel", back_populates="team_members")


class TeamMemberBase(BaseModel):
    user_id: int
    team_id: int
    role: constr(max_length=50)


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMember(TeamMemberBase):
    id: int
    joined_at: datetime

    class Config:
        orm_mode = True


class TeamsMembers(Template):
    def __init__(self, db, Schema: str = "SCHEMA"):
        schemas = {
            "BASE": TeamMemberModel,
            "CREATE": TeamMemberCreate,
            "SCHEMA": TeamMember,
        }
        super().__init__(
            Model=TeamMemberModel, db=db, Schema=schemas.get(Schema, TeamMember)
        )

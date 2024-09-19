"""Model for Activity Log"""

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


class ActivityLogModel(database.BASE):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(
        Integer,
        ForeignKey("teams.id", ondelete="NO ACTION", onupdate="NO ACTION"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="NO ACTION", onupdate="NO ACTION"),
        nullable=True,
    )
    action = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    ip_address = Column(String(45))

    team = relationship("TeamModel", back_populates="activity_logs")
    user = relationship("UserModel", back_populates="activity_logs")


class ActivityLogBase(BaseModel):
    team_id: int
    user_id: Optional[int]
    action: str
    ip_address: Optional[constr(max_length=45)]


class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLog(ActivityLogBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class ActivitiesLog(Template):
    def __init__(
        self,
        db,
        Schema="SCHEMA",
    ) -> None:
        schemas = {
            "BASE": ActivityLogBase,
            "CREATE": ActivityLogCreate,
            "SCHEMA": ActivityLog,
        }
        super().__init__(
            Model=ActivityLogModel, Schema=schemas.get(Schema, ActivityLog), db=db
        )

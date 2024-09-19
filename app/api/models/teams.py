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


class TeamModel(database.BASE):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), nullable=False)
    stripe_customer_id = Column(Text, unique=True)
    stripe_subscription_id = Column(Text, unique=True)
    stripe_product_id = Column(Text)
    plan_name = Column(String(50))
    subscription_status = Column(String(20))

    activity_logs = relationship("ActivityLogModel", back_populates="team")
    invitations = relationship("InvitationModel", back_populates="team")
    team_members = relationship("TeamMemberModel", back_populates="team")


# Team Model
class TeamBase(BaseModel):
    name: constr(max_length=100)


class TeamCreate(TeamBase):
    pass


class Team(TeamBase):
    id: int
    created_at: datetime
    updated_at: datetime
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    stripe_product_id: Optional[str]
    plan_name: Optional[constr(max_length=50)]
    subscription_status: Optional[constr(max_length=20)]

    class Config:
        orm_mode = True


class Teams(Template):
    def __init__(self, db, Schemas: str = "SCHEMA"):
        schemas = {"BASE": TeamModel, "CREATE": TeamCreate, "SCHEMA": Team}
        super().__init__(Model=TeamModel, db=db, Schema=schemas.get(Schemas, Team))

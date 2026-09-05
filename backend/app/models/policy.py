from sqlalchemy import Column, Integer, String, Text, Boolean, Enum as SQLEnum
from app.database.session import Base
from app.models.enums import PriorityLevel

class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    rule_type = Column(String(50), nullable=False, index=True)
    rule_config = Column(Text, nullable=False)  # JSON-encoded configuration
    priority = Column(SQLEnum(PriorityLevel), default=PriorityLevel.MEDIUM, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

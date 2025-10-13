from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime

from ...database import Base


class ClaimModel(Base):
    __tablename__ = 'claims'

    id = Column(Integer, primary_key=True)
    patent_id = Column(
        Integer,
        ForeignKey('patents.id'),
        nullable=True,
    )
    patent_application_id = Column(
        Integer,
        ForeignKey('patent_applications.id'),
        nullable=True,
    )
    claim_number = Column(Integer, nullable=False)
    claim_text = Column(Text, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (
        UniqueConstraint('patent_id', 'claim_number'),
        UniqueConstraint('patent_application_id', 'claim_number'),
    )

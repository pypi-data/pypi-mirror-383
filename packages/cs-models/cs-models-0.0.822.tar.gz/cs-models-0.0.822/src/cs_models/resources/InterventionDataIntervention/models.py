from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Float,
    Boolean,
)

from ...database import Base


class InterventionDataInterventionModel(Base):
    __tablename__ = "intervention_data_intervention"

    id = Column(Integer, primary_key=True)
    intervention_data_id = Column(
        Integer,
        ForeignKey('intervention_data.id'),
        nullable=False,
    )
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    score = Column(
        Float,
        nullable=False,
    )
    date = Column(DateTime, nullable=True)
    preferred = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint('intervention_data_id', 'intervention_id'),)

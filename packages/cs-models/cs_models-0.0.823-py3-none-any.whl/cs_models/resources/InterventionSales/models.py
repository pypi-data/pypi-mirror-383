from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    UniqueConstraint,
    ForeignKey,
    Boolean,
    Float,
)

from ...database import Base


class InterventionSalesModel(Base):
    __tablename__ = "intervention_sales"

    id = Column(Integer, primary_key=True)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    sales_table_id = Column(
        Integer,
        ForeignKey('sales.id'),
        nullable=False,
    )
    score = Column(
        Float,
        nullable=False,
    )
    is_deleted = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("intervention_id", "sales_table_id"),)

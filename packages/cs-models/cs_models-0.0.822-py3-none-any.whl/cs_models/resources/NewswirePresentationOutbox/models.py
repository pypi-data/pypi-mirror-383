from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Boolean,
)
from datetime import datetime

from ...database import Base


class NewswirePresentationOutboxModel(Base):
    __tablename__ = 'newswire_presentation_outbox'

    id = Column(Integer, primary_key=True)
    news_id = Column(
        Integer,
        nullable=False,
        index=True,
    )
    submitted = Column(Boolean, nullable=True)
    historical = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

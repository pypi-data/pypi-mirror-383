from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    UniqueConstraint,
    ForeignKey,
    Boolean,
)
from datetime import datetime

from ...database import Base


class PatentModel(Base):
    __tablename__ = 'patents'

    id = Column(Integer, primary_key=True)
    patent_number = Column(String(128), nullable=False, index=True)
    jurisdiction = Column(String(128), nullable=False)
    patent_application_id = Column(
        Integer,
        ForeignKey('patent_applications.id'),
        nullable=True,
    )
    appl_id = Column(String(128))
    app_grp_art_number = Column(String(128))
    app_type = Column(String(128))
    country_code = Column(String(128))
    document_number = Column(String(128))
    kind_code = Column(String(128))
    primary_identifier = Column(String(256))
    abstract_text = Column(Text)
    description = Column(Text)
    applicant = Column(Text)
    inventors = Column(Text)
    title = Column(String(256))
    url = Column(String(500))
    app_class = Column(String(20))
    app_sub_class = Column(String(20))
    grant_date = Column(DateTime)
    submission_date = Column(DateTime)
    app_filing_date = Column(DateTime)
    app_status_date = Column(DateTime)
    app_early_pub_date = Column(DateTime)
    filing_date_us = Column(DateTime)
    expiration_date = Column(DateTime)
    pto_adjustments = Column(String(10))
    appl_delay = Column(String(10))
    total_pto_days = Column(String(10))
    assignee = Column(Text)
    patent_pdf_url = Column(String(500))
    espace_url = Column(String(500))
    docdb_family_id = Column(Integer)
    inpadoc_family_id = Column(Integer)
    is_orange_book = Column(Boolean, nullable=True)
    is_purple_book = Column(Boolean, nullable=True)

    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint('patent_number', 'jurisdiction'),)

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
)
from datetime import datetime
from ...database import Base


class PubmedModel(Base):
    __tablename__ = 'pubmed'

    id = Column(Integer, primary_key=True)
    pubmed_id = Column(Integer, nullable=True)
    doi = Column(String(128), nullable=True)
    type = Column(String(20), nullable=True)
    publication_type = Column(Text, nullable=True)
    date = Column(DateTime, nullable=True)
    date_created = Column(DateTime, nullable=True)
    date_completed = Column(DateTime, nullable=True)
    date_revised = Column(DateTime, nullable=True)
    journal_issn = Column(String(50), nullable=True)
    journal_volume = Column(String(50), nullable=True)
    journal_issue = Column(String(50), nullable=True)
    journal_title = Column(String(255), nullable=True)
    journal_title_iso_abbrev = Column(String(191), nullable=True)
    outbound_ref_count = Column(Integer, nullable=True)
    inbound_ref_count = Column(Integer, nullable=True)
    orig_file_url = Column(String(255), nullable=True)
    best_oa_location = Column(String(255), nullable=True)
    method = Column(String(50), nullable=True)
    verification = Column(String(50), nullable=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    author_list = Column(Text, nullable=True)
    keyword_list = Column(Text, nullable=True)
    chemical_list = Column(Text, nullable=True)
    mesh_list = Column(Text, nullable=True)
    coi_statement = Column(Text, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

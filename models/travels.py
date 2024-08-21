from sqlalchemy.orm import mapped_column
from sqlalchemy import Column, VARCHAR, TEXT, BOOLEAN, ForeignKey, FLOAT, DATE

from models.base import BaseModel


class Travel(BaseModel):
    __tablename__ = 'travels'

    title = Column(VARCHAR(255), nullable=False)
    description = Column(TEXT(), nullable=True)
    is_archived = Column(BOOLEAN(), nullable=False, default=False)
    user_id = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"))


class Location(BaseModel):
    __tablename__ = 'locations'
    country = Column(VARCHAR(255), nullable=False)
    city = Column(VARCHAR(255), nullable=False)
    lat = Column(FLOAT(), nullable=False)
    long = Column(FLOAT(), nullable=False)
    date_start = Column(DATE(), nullable=False)
    date_end = Column(DATE(), nullable=False)
    travel_id = mapped_column(ForeignKey("travels.id", ondelete="CASCADE"))


class TravelPartner(BaseModel):
    __tablename__ = 'travelpartners'
    user_id = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"))
    travel_id = mapped_column(ForeignKey("travels.id", ondelete="CASCADE"))


class TravelNote(BaseModel):
    __tablename__ = 'travelnotes'
    author_id = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"))
    travel_id = mapped_column(ForeignKey("travels.id", ondelete="CASCADE"))
    is_public = Column(BOOLEAN(), nullable=False)
    title = Column(VARCHAR(255), nullable=False)
    text = Column(TEXT(), nullable=True)


class NoteAttachment(BaseModel):
    __tablename__ = 'noteattachments'
    note_id = mapped_column(ForeignKey("travelnotes.id", ondelete="CASCADE"))
    photo_telegram_id = Column(VARCHAR(255), nullable=True)
    video_telegram_id = Column(VARCHAR(255), nullable=True)
    file_telegram_id = Column(VARCHAR(255), nullable=True)


class Debt(BaseModel):
    __tablename__ = 'debts'
    debtor_id = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"))
    creditor_id = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"))
    travel_id = mapped_column(ForeignKey("travels.id", ondelete="CASCADE"))
    money = Column(FLOAT(), nullable=False)

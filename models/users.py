from sqlalchemy.orm import mapped_column
from sqlalchemy import Column, VARCHAR, TEXT, FLOAT, INTEGER, BOOLEAN, BigInteger, ForeignKey
from models.base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    first_name = Column(VARCHAR(255), nullable=False)
    last_name = Column(VARCHAR(255), nullable=True)
    bio = Column(TEXT(), nullable=True)
    country = Column(VARCHAR(100), nullable=False)
    city = Column(VARCHAR(255), nullable=False)
    lat = Column(FLOAT(), nullable=False)
    long = Column(FLOAT(), nullable=False)
    age = Column(INTEGER(), nullable=False)
    is_male = Column(BOOLEAN(), nullable=False)
    looking_for_a_partner = Column(BOOLEAN(), nullable=False)
    telegram_id = Column(BigInteger(), nullable=False, unique=True)


class Interest(BaseModel):
    __tablename__ = 'interests'
    title = Column(VARCHAR(100), nullable=False)
    user_id = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"))

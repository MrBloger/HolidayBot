from typing import Annotated, Optional

# from datetime import date

from sqlalchemy import BigInteger, Column, Date, ForeignKey, Table, MetaData

from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

intpk = Annotated[int, mapped_column(primary_key=True)]


# Модель мероприятия
class Event(Base):
    __tablename__ = "events"
    
    id: Mapped[intpk]
    title: Mapped[str]
    date: Mapped[Date] = mapped_column(Date)
    creator_id = Column(BigInteger, nullable=False)
    
    #Связь с участниками
    participants: Mapped[list["Participant"]] = relationship(
        back_populates="event"
    )

# Модель участников
class Participant(Base):
    __tablename__ = "participants"
    
    id: Mapped[intpk]
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    # user_id: Mapped[int]
    username: Mapped[str]
    # status: Mapped[str] = mapped_column(default="не подтвержден")
    
    # Связь с мероприятием
    event: Mapped[list["Event"]] = relationship(
        back_populates="participants"
    )
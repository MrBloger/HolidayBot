from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import Integer, and_, cast, delete, func, insert, inspect, or_, select, text
from sqlalchemy.orm import aliased, contains_eager, joinedload, selectinload

from database.database import Base
from .models import Event, Participant



# Создает мероприятие пользователя
async def create_event(session: AsyncSession, event_name: str, event_date: str, creator_id: int):
    async with session.begin():
        new_event = Event(title=event_name, date=event_date, creator_id=creator_id)
        session.add(new_event)



# Выдает список мероприятий пользователя
async def get_events(session: AsyncSession, creator_id: int):
    async with session as session:
        result = await session.execute(
            select(Event)
            .where(Event.creator_id == creator_id))
        return result.scalars().all()


# Выдает список мероприятий для изменения
async def edit_events(session: AsyncSession, event_id: int):
    async with session as session:
        result = await session.execute(
            select(Event)
            .where(Event.id == event_id))
        return result.scalars().first()


# Создает участника для мероприятия пользователя
async def create_participants(session: AsyncSession, event_id: int, participant_name: str):
    async with session.begin():
        
        new_participant = Participant(event_id=event_id, username=participant_name)
        session.add(new_participant)
        
        result = await session.execute(
            select(Event)
            .options(selectinload(Event.participants))
            .where(Event.id == event_id)
        )
        
    return result.scalars().first()


# Выдает список мероприятий с его участниками
async def get_participants_for_event(session: AsyncSession, event_id: int):
    async with session as session:
        result = await session.execute(
            select(Participant)
            .options(selectinload(Participant.event))
            .where(Participant.event_id == event_id)
        )
    
    return result.scalars().all()


# Удаляет мероприятие и участников вместе с ним
async def delete_events(session: AsyncSession, creator_id: int, event_id: int):
    async with session.begin():
        await session.execute(
            delete(Event)
            .where(Event.id == event_id, Event.creator_id == creator_id)
        )
        await session.commit()

# Удаляет участников из мероприятия
async def delete_participants(session: AsyncSession, participant_id: int, event_id: int):
    async with session.begin():
        await session.execute(
            delete(Participant)
            .where(Participant.id == participant_id, Participant.event_id == event_id)
        )
        await session.commit()

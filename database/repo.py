from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Results
from datetime import datetime


class ResultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: str, result: str, time_create: datetime = None):
        """Создание новой записи."""
        if time_create is None:
            time_create = datetime.now()

        db_result = Results(data=data, result=result, time_create=time_create)
        self.session.add(db_result)
        await self.session.commit()
        await self.session.refresh(db_result)
        print(db_result)
        return db_result

    async def get_by_id(self, result_id: int):
        """Получение записи по ID."""
        query = select(Results).where(Results.id == result_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_data(self, data: dict):
        """Получение записи по data."""
        query = select(Results).where(Results.data == str(data))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self):
        """Получение всех записей."""
        query = select(Results)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, result_id: int, data: str = None, result: str = None):
        """Обновление записи."""
        db_result = await self.get_by_id(result_id)
        if not db_result:
            return None

        if data is not None:
            db_result.data = data
        if result is not None:
            db_result.result = result

        await self.session.commit()
        await self.session.refresh(db_result)
        return db_result

    async def delete(self, result_id: int):
        """Удаление записи."""
        db_result = await self.get_by_id(result_id)
        if db_result:
            await self.session.delete(db_result)
            await self.session.commit()
            return True
        return False

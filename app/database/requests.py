from app.database.models import async_session
from app.database.models import User
from sqlalchemy import select, update
from app.constants import HUMANITARIAN

import random

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, is_banned=False, task_type="", task="", answer=""))
            await session.commit()

async def get_user(tg_id):
    async with async_session() as session:
        if await session.scalar(select(User).where(User.tg_id == tg_id)) is None:
            await set_user(tg_id)
        return await session.scalar(select(User).where(User.tg_id == tg_id))

async def ban_user(tg_id):
    async with async_session() as session:
        task_type = random.choice(["humiliate", "calculate"])
        if task_type == "humiliate":
            upd = update(User).where(User.tg_id == tg_id).values(is_banned=True, task_type="humiliate",
                                                                 task=HUMANITARIAN, answer=HUMANITARIAN)
            await session.execute(upd)
            await session.commit()
        elif task_type == "calculate":
            numbers = [random.randint(1, 99) for i in range(random.randint(2, 5))]
            tsk = str(numbers[0])
            for i in range(1, len(numbers)):
                tsk += random.choice(["+", "-"]) + str(numbers[i])

            upd = update(User).where(User.tg_id == tg_id).values(is_banned=True, task_type="calculate",
                                                                 task=tsk, answer=str(eval(tsk)))
            await session.execute(upd)
            await session.commit()

async def unban_user(tg_id):
    async with async_session() as session:
        upd = update(User).where(User.tg_id == tg_id).values(is_banned=False)
        await session.execute(upd)
        await session.commit()

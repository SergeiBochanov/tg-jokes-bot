import random
import pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from aiogram.types import Message

scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Omsk'))

class Events(StatesGroup):
    clowns_isActive = State()
    random_react_isActive = State()
    clear_isActive = State()

events_list = [Events.clowns_isActive, Events.random_react_isActive, Events.clear_isActive]
data = {'hour': 17, 'minute': 0}

async def setNewEvent(state: FSMContext):
    if random.random() < 0.2:
        current_event = random.choice(events_list)
        await state.set_state(current_event)

async def state_reset(state: FSMContext):
    await state.clear()

async def reset_planning(state: FSMContext):
    if scheduler.get_job(job_id="stop") is None:
        scheduler.add_job(state_reset, "date", run_date=datetime.now(pytz.timezone('Asia/Omsk')) + timedelta(minutes=5), id="stop", args=(state, ))

async def events_scheduler_func(message: Message, state: FSMContext):
    if scheduler.running:
        scheduler.shutdown()
        await message.answer("Events apperance: <b>off</b>", parse_mode='html')
    else:
        scheduler.add_job(setNewEvent, 'cron', hour=data['hour'], minute=data['minute'], args=(state, ))
        scheduler.start()
        await message.answer("Events appearance: <b>on</b>", parse_mode='html')

async def event_update_data(hour, minute):
    data['hour'] = hour
    data['minute'] = minute
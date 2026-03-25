from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message, ChatPermissions
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.events import Events, event_update_data
from app.postcards import update_time
from app.constants import CUSTOM_TITLE_PREFIX
from dotenv import load_dotenv

import os

load_dotenv()
bot = Bot(os.getenv('TOKEN'))

allowed_users = [int(os.getenv('KOLYA_ID')), int(os.getenv('SEVWAY_ID'))]
abused_users = [int(os.getenv('VLAD_ID')), int(os.getenv('PASHA_ID')), int(os.getenv('ANTON_ID'))]

admin_router = Router()

class States(StatesGroup):
    entering_task = State()
    entering_day = State()
    entering_hour = State()
    entering_minute = State()

@admin_router.message(Command('admin'))
async def clowns_start(message: Message):
    if message.from_user.id in allowed_users:
        await message.answer('Доступные команды: \n/clowns_start - запуск ивента клоуна'
                             '\n/random_start - запуск ивента рандомных реактов'
                             '\n/event_clear - отмена всех ивентов, стоящих в очереди (и идущих)'
                             '\n/mute - замутить бедолаг'
                             '\n/unmute - размутить бедолаг с выдачей админок'
                             '\n/update_time - поменять время работы запланированных задач')

@admin_router.message(Command('clowns_start'))
async def clowns_start(message: Message, state: FSMContext):
    if message.from_user.id in allowed_users:
        await state.set_state(Events.clowns_isActive)
        await message.answer('Клоуны активированы')

@admin_router.message(Command('random_start'))
async def random_start(message: Message, state: FSMContext):
    if message.from_user.id in allowed_users:
        await state.set_state(Events.random_react_isActive)
        await message.answer('Случайные реакции активированы')

@admin_router.message(Command('event_clear'))
async def clowns_start(message: Message, state: FSMContext):
    if message.from_user.id in allowed_users:
        await state.clear()
        await message.answer('Все события отключены')

@admin_router.message(Command('mute'))
async def mute(message: Message):
    if message.from_user.id in allowed_users:
        for user in abused_users:
            await bot.restrict_chat_member(message.chat.id, user, ChatPermissions(can_send_messages=False))
        await message.reply("Отправка сообщений ограничена")

@admin_router.message(Command('unmute'))
async def unmute(message: Message):
    if message.from_user.id in allowed_users:
        for user in abused_users:
            await bot.restrict_chat_member(message.chat.id, user, ChatPermissions(can_send_messages=True))
            await bot.promote_chat_member(message.chat.id, user,
                                          can_delete_messages=True,
                                          can_manage_video_chats=True,
                                          can_invite_users=True,
                                          can_pin_messages=True)
        await message.reply("Отправка сообщений разрешена, участники восстановлены в правах")

@admin_router.message(Command('update_time'))
async def update(message: Message, state: FSMContext):
    if message.from_user.id in allowed_users:
        await message.answer('Что вы хотите изменить?\n'
                             '1 - Отправка открыток по утрам\n'
                             '2 - Отправка гифок по воскресеньям\n'
                             '3 - Время активации ивентов')
        await state.set_state(States.entering_task)

@admin_router.message(States.entering_task)
async def change_postcards(message: Message, state: FSMContext):
    await state.update_data(task=message.text)
    if message.text == '2':
        await state.set_state(States.entering_day)
        await message.answer('Окей, теперь отправь день выполнения от 1 до 7, где 1 - понедельник, 7 - воскресенье')
    else:
        await state.set_state(States.entering_hour)
        await message.answer(
            'Окей, теперь отправь час, в который будет выполняться действие (в 24-часовом формате, от 0 до 23)')

@admin_router.message(States.entering_day)
async def change_postcards(message: Message, state: FSMContext):
    await state.update_data(day=message.text)
    await state.set_state(States.entering_hour)
    await message.answer(
        'Окей, теперь отправь час, в который будет выполняться действие (в 24-часовом формате, от 0 до 23)')

@admin_router.message(States.entering_hour)
async def change_postcards(message: Message, state: FSMContext):
    await state.update_data(hour=message.text)
    await state.set_state(States.entering_minute)
    await message.answer('Окей, теперь отправь минуту, в которую будет выполняться действие (от 0 до 59)')

@admin_router.message(States.entering_minute)
async def change_postcards(message: Message, state: FSMContext):
    await state.update_data(minute=message.text)
    data = await state.get_data()
    if data['task'] == '1':
        await update_time('postcards', -1, int(data['hour']), int(data['minute']))
        await message.answer('Дело сделано :)')
    elif data['task'] == '2':
        await update_time('sun_gif', int(data['day']) - 1, int(data['hour']), int(data['minute']))
        await message.answer('Дело сделано :)')
    elif data['task'] == '3':
        await event_update_data(int(data['hour']), int(data['minute']))
        await message.answer('Дело сделано, теперь перезапусти планировщик командой /event_switch')
    await state.clear()

from time import sleep

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReactionTypeEmoji, ContentType
from aiogram.types import FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.parsers import (parser, image_parser, video_parser, get_image,
                         get_video, get_tg_last_post_id, nazhor_parser)
from app.middlewares import BanMiddleware, UnbanMiddleware, ReactMiddleware
from app.events import Events, reset_planning, events_scheduler_func
from dotenv import load_dotenv
from app.constants import (RANDOM_JOKE_URL, JEW_JOKE_URL, ARMY_JOKE_URL, WOMAN_JOKE_URL,
                           RANDOM_REACT_EMOJI, BAN_COMMAND_ANSWER, BAN_COMMAND_MESSAGE, 
                           CHESS_JOKE_URL, UNBAN_COMMAND_ANSWER)
from app.postcards import nazhor_subtract, nazhor_current

import os
import random
import app.database.requests as rq

load_dotenv()
chat_id = int(os.getenv('CHAT_ID'))
vlad = int(os.getenv('VLAD_ID'))
kolya = int(os.getenv('KOLYA_ID'))
pasha = int(os.getenv('PASHA_ID'))
anton = int(os.getenv('ANTON_ID'))
sevway = int(os.getenv('SEVWAY_ID'))

router = Router()

router.message.outer_middleware(ReactMiddleware())
router.message.outer_middleware(UnbanMiddleware())
router.message.middleware(BanMiddleware())

list_of_woman_jokes = parser(WOMAN_JOKE_URL + str(random.randint(1, 85)) + '?type=anekdots')
list_of_jew_jokes = parser(JEW_JOKE_URL + str(random.randint(1, 50)))
list_of_army_jokes = parser(ARMY_JOKE_URL + str(random.randint(1, 100)))
list_of_chess_jokes = parser(CHESS_JOKE_URL + str(random.randint(1, 13)))
random.shuffle(list_of_jew_jokes)
random.shuffle(list_of_army_jokes)
list_of_jokes = parser(RANDOM_JOKE_URL)
random.shuffle(list_of_jokes)

@router.message(CommandStart())
async def start(message: Message):
    await message.answer('Бот готов к работе!')

@router.message(Command('joke'))
async def joke(message: Message):
    if len(list_of_jokes) == 0:
        list_of_jokes.append(parser(RANDOM_JOKE_URL)[0])
    await message.answer(list_of_jokes[0])
    del list_of_jokes[0]

@router.message(Command('jewjoke'))
async def jew_joke(message: Message):
    if len(list_of_jew_jokes) == 0:
        list_of_jew_jokes.append(parser(JEW_JOKE_URL + str(random.randint(1, 50)))[0])
    await message.answer(list_of_jew_jokes[0])
    del list_of_jew_jokes[0]

@router.message(Command('armyjoke'))
async def army_joke(message: Message):
    if len(list_of_army_jokes) == 0:
        list_of_army_jokes.append(parser(ARMY_JOKE_URL + str(random.randint(1, 100)))[0])
    await message.answer(list_of_army_jokes[0])
    del list_of_army_jokes[0]

@router.message(Command('womanjoke'))
async def woman_joke(message: Message):
    if len(list_of_woman_jokes) == 0:
        list_of_woman_jokes.append(parser(WOMAN_JOKE_URL)[0])
    await message.answer(list_of_woman_jokes[0])
    del list_of_woman_jokes[0]

@router.message(Command('chessjoke'))
async def woman_joke(message: Message):
    if len(list_of_chess_jokes) == 0:
        list_of_chess_jokes.append(parser(CHESS_JOKE_URL + str(random.randint(1, 13)))[0])
    await message.answer(list_of_chess_jokes[0])
    del list_of_chess_jokes[0]

@router.message(Command('gif'))
async def random_gif(message: Message):
    last_post_id = get_tg_last_post_id('https://t.me/s/gifachannel', 'video')
    random_gif_url = video_parser(f"https://t.me/gifachannel/{random.randint(1, last_post_id)}?embed=1")
    if random_gif_url is None:
        await random_gif(message)
    else:
        result_gif = await get_video(random_gif_url)
        await message.answer_animation(result_gif)

@router.message(Command('image'))
async def random_image(message: Message):
    last_post_id = get_tg_last_post_id('https://t.me/s/karkkkb', 'image')
    random_image_url = image_parser(f"https://t.me/karkkkb/{random.randint(1, last_post_id)}?embed=1")
    if random_image_url is None:
        await random_image(message)
    else:
        result_image = await get_image(random_image_url)
        await message.answer_photo(result_image)

@router.message(Command('video'))
async def random_video(message: Message):
    last_post_id = get_tg_last_post_id('https://t.me/s/vidoskb', 'video')
    random_video_url = video_parser(f"https://t.me/vidoskb/{random.randint(1, last_post_id)}?embed=1")
    if random_video_url is None:
        await random_video(message)
    else:
        result_video = await get_video(random_video_url)
        await message.answer_video(result_video)

@router.message(Command('kitty'))
async def random_kitty(message: Message):
    last_post_id = get_tg_last_post_id('https://t.me/s/kittensandquotes', 'image')
    random_image_url = image_parser(f'https://t.me/kittensandquotes/{random.randint(2272, last_post_id)}?embed=1')
    if random_image_url is None:
        await random_kitty(message)
    else:
        result_image = await get_image(random_image_url)
        await message.answer_photo(result_image)

@router.message(Command('nazhor'))
async def random_nazhor(message: Message):
    if message.from_user.id == pasha:
        nazhor_balance = await nazhor_current()
        if nazhor_balance > 0:
            if random.random() < 0.95:
                await message.reply_photo(FSInputFile(f'resource/nazhor/{random.randint(0, 13)}.jpg'))
            else:
                await message.reply_sticker(FSInputFile(f'resource/nazhor/nazhor_fail.png'))
            await nazhor_subtract()
        else:
            await message.reply('Лимит нажора на сегодня исчерпан')
    else:
        random_nazhor_url = nazhor_parser(f'https://ru.freepik.com/photos/restaurant-food/{random.randint(0, 100)}')
        if random_nazhor_url is None:
            await random_nazhor(message)
        else:
            result_nazhor_image = await get_image(random_nazhor_url)
            await message.reply_photo(result_nazhor_image)

@router.message(Command('jewmoment'))
async def jew_moment(message: Message):
    await message.answer_voice(FSInputFile('resource/jewmoment.mp3'))

@router.message(Command("ban"))
async def ban(message: Message):
    if message.from_user.id in [vlad, kolya, sevway]:
        await rq.set_user(pasha)
        await rq.set_user(anton)
        await rq.ban_user(pasha)
        await rq.ban_user(anton)
        await message.answer(BAN_COMMAND_ANSWER)
    else:
        await message.answer(BAN_COMMAND_MESSAGE, parse_mode='html')

@router.message(Command("unban"))
async def ban(message: Message):
    if message.from_user.id in [vlad, kolya, sevway]:
        await rq.set_user(pasha)
        await rq.set_user(anton)
        await rq.unban_user(pasha)
        await rq.unban_user(anton)
        await message.answer(UNBAN_COMMAND_ANSWER)
    else:
        await message.answer(BAN_COMMAND_MESSAGE, parse_mode='html')

@router.message(Command("game"))
async def pixel_rush(message: Message):
    await message.answer_game(game_short_name="pixelrush")

@router.callback_query(lambda c: c.game_short_name == 'pixelrush')
async def process_callback_play_game(callback_query: CallbackQuery):
    game_url = f'https://pixelrush.onrender.com?user_id={callback_query.from_user.id}&chat_id={callback_query.message.chat.id}&message_id={callback_query.message.message_id}'
    await callback_query.answer(url=game_url)

@router.message(Events.clowns_isActive)
async def clowns_event(message: Message, state: FSMContext):
    if message.chat.id == chat_id:
        await reset_planning(state)
        await message.react([ReactionTypeEmoji(emoji='🤡')])

@router.message(Events.random_react_isActive)
async def random_react_event(message: Message, state: FSMContext):
    if message.chat.id == chat_id:
        await reset_planning(state)
        random_emoji = random.choice(RANDOM_REACT_EMOJI)
        await message.react([ReactionTypeEmoji(emoji=random_emoji)])

@router.message(Command('event_switch'))
async def test(message: Message, state: FSMContext):
    await events_scheduler_func(message, state)

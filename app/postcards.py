import aiohttp
import random
import os
import pytz

from app.parsers import video_parser, good_morning_parser, get_image, get_video, get_tg_last_post_id
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import BufferedInputFile
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
chat_id = os.getenv('CHAT_ID')

scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Omsk'))

nazhor_count = random.randint(5, 10)

async def sunday_gif():
    last_post_id = get_tg_last_post_id('https://t.me/s/dankpostcards', 'video')
    random_gif_url = video_parser(f"https://t.me/dankpostcards/{random.randint(1, last_post_id)}?embed=1")
    if random_gif_url is None:
        await sunday_gif()
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(random_gif_url) as response:
                bin_gif = await response.read()

        result_gif = BufferedInputFile(file=bin_gif, filename=f'your-gif-{random.randint(0, 100_000)}.mp4')
        await bot.send_animation(chat_id, result_gif)

async def everyday_greeting():
    parse_result: list[str] = good_morning_parser(f"https://3d-galleru.ru/archive/cat/dobroe-utro-60/page-{random.randint(1, 1147)}/")
    if parse_result is None:
        await everyday_greeting()
    else:
        url = parse_result[0]
        file_extension = parse_result[1]
        if file_extension == "img":
            result_image = await get_image(url)
            await bot.send_photo(chat_id, result_image)
        elif file_extension == "gif":
            result_gif = await get_video(url)
            await bot.send_animation(chat_id, result_gif)
        else:
            result_video = await get_video(url)
            preview = await get_image(parse_result[2])
            await bot.send_video(chat_id, result_video, thumbnail=preview)

async def nazhor_subtract():
    global nazhor_count
    nazhor_count -= 1

async def nazhor_current():
    global nazhor_count
    return nazhor_count

async def nazhor_reset():
    global nazhor_count
    nazhor_count = random.randint(5, 10)
    print(f'Nazhor reset with count: {nazhor_count}')


async def scheduler_func():
    if scheduler.running:
        scheduler.shutdown()
    scheduler.add_job(sunday_gif, 'cron', day_of_week=6, hour=10, id='sun_gif')
    scheduler.add_job(everyday_greeting, 'cron', hour=7, id='postcards')
    scheduler.add_job(nazhor_reset, 'cron', hour=0, id='nazhor_reset')
    scheduler.start()

async def update_time(task, day, hour_, minute_):
    if task == 'sun_gif':
        scheduler.reschedule_job(job_id='sun_gif', trigger='cron', day_of_week=day, hour=hour_, minute=minute_)
    elif task == 'postcards':
        scheduler.reschedule_job(job_id='postcards', trigger='cron', hour=hour_, minute=minute_)
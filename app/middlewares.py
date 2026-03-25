from random import randint
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, ReactionTypeEmoji, FSInputFile
from typing import Callable, Dict, Any, Awaitable
from app.constants import (BANNED_RESPONSE, UNBAN_MESSAGE, GM_GN_WORDS, SUP_WORDS, POST_IRONY, STIPEND)

import app.database.requests as rq

class BanMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        user = await rq.get_user(event.from_user.id)
        if user.is_banned:
            response = BANNED_RESPONSE
            if user.task_type == "humiliate":
                response += f'напишите "{user.task}"'
            elif user.task_type == "calculate":
                response += f"посчитайте, чему равно {user.task}"
            await event.reply(response)
        else:
            return await handler(event, data)

class UnbanMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        user = await rq.get_user(event.from_user.id)
        if user.is_banned:
            if event.text.lower() == user.answer and not event.forward_from:
                await event.react([ReactionTypeEmoji(emoji='👍')])
                await rq.unban_user(event.from_user.id)
                await event.reply(UNBAN_MESSAGE)
        return await handler(event, data)

class ReactMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        # single-word trigger
        if "тюкал" in event.text.lower():
            await event.reply_sticker(FSInputFile('resource/motherland.webm'))
        if "сигм" in event.text.lower():
            await event.reply_voice(FSInputFile('resource/sigma.mp3'))
        if "модер" in event.text.lower():
            await event.reply_video(FSInputFile('resource/hello_moderator.mp4'))
        if "общага" in event.text.lower():
            await event.reply_sticker(FSInputFile('resource/barrack.webm'))
        if "созвон" in event.text.lower():
            await event.reply_sticker(FSInputFile(f'resource/call/{randint(0, 7)}.webm'))
        # set-words trigger
        if [i for i in GM_GN_WORDS if i in event.text.lower()] or [j for j in SUP_WORDS if event.text.lower() == j]:
            await event.react([ReactionTypeEmoji(emoji='❤')])
        if [i for i in POST_IRONY if i in event.text.lower()]:
            await event.reply_video(FSInputFile('resource/postirony.mp4'))
        if [i for i in STIPEND if i in event.text.lower()] and "пришл" in event.text.lower():
            await event.reply_sticker(FSInputFile('resource/stipend.jpg'))
        # equal-word trigger
        if event.text.lower() == "да":
            await event.reply_sticker(FSInputFile('resource/kirkorov.png'))
        if event.text.lower() == "нет":
            await event.reply('Гуманитария ответ 🤭😜')
        return await handler(event, data)
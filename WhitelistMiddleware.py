from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from credentials import whitelist


class WhitelistMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if event.chat.id in whitelist:
            return await handler(event, data)
        await event.answer(
            "У вас нет доступа!"
        )
        return

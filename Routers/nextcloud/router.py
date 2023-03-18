from aiogram import Router

from aiogram.types import Message
from aiogram import F

# Local imports
# from Buttons import Buttons
# from vars.credentials import EMAIL, CF_API_TOKEN
# from vars.replies import record_reply, sure_reply

nextcloud_router = Router()

'''
    Pic
'''


@nextcloud_router.message(F.photo)
async def upload_media(message: Message) -> None:
    await message.answer(text='Media uploaded')

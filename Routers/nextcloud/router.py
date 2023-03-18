from aiogram import Router

from aiogram.types import CallbackQuery
from aiogram import F

# Local imports
# from Buttons import Buttons
# from vars.credentials import EMAIL, CF_API_TOKEN
# from vars.replies import record_reply, sure_reply

nextcloud_router = Router()


'''
    Pic
'''


@nextcloud_router.callback_query(F.photo)
async def upload_media(callback: CallbackQuery) -> None:
    await callback.message.answer('Media uploaded')
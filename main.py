import asyncio
import logging
from logging import INFO
from CloudFlare import CloudFlare
from aiogram import Bot, Dispatcher
from aiogram.filters import Text, Command
from aiogram.types import CallbackQuery, Message
# Local imports
from Buttons import Buttons
from replies import main_reply
from Routers.dns.dns_router import dns_router
from Middleware import WhitelistMiddleware
from credentials import EMAIL, CF_API_TOKEN, TG_API_TOKEN
from Routers.dns.add_rec_router import dns_add_rec_form


# Tuples
main_buttons = ('DNS', 'WireGuard')

# Configure logging
logging.basicConfig(level=INFO)

# Cloudflare https://github.com/cloudflare/python-cloudflare
cf = CloudFlare(email=EMAIL, key=CF_API_TOKEN)

# Initialize bot and dispatcher 
bot = Bot(token=TG_API_TOKEN, parse_mode="HTML")
dp = Dispatcher()


dns_router.include_router(dns_add_rec_form)
dp.include_router(dns_router)
dp.message.outer_middleware(WhitelistMiddleware())

'''
    Commands
'''


@dp.message(Command(commands=['id', 'getid', 'get_id']))
async def send_id(message: Message) -> None:
    await message.reply(str(message.chat.id))


@dp.callback_query(Text(startswith="WireGuard"))
async def wg(callback: CallbackQuery) -> None:
    await bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id)
    await callback.message.edit_text('Заглушка', reply_markup=Buttons.main_menu())


'''
    Main Menu
'''


@dp.message(Command(commands=['start', 'help', 'menu', 'home']))
async def send_welcome(message: Message) -> None:
    await message.answer(main_reply, reply_markup=Buttons.main_menu())
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@dp.callback_query(Text(startswith='menu'))
async def menu_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(main_reply, reply_markup=Buttons.main_menu())
    await callback.answer()


'''
    Main()
'''


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import os
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_IDS = list(map(int, os.getenv("MANAGER_IDS", "").split(",")))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
awaiting_reply = {}

@router.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    await message.answer("Здравствуйте! Чем могу помочь?")
    await message.answer("Подождите, я ищу вашу заявку в базе данных. Если у меня не получится найти вас, с вами свяжутся!")
    
    if MANAGER_IDS:
        manager_id = MANAGER_IDS[0]
        awaiting_reply[manager_id] = user_id
        try:
            await bot.forward_message(manager_id, user_id, message.message_id)
            user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"
            await bot.send_message(manager_id, f"📩 Новый запрос от {user_info}")
        except Exception as e:
            print("Ошибка отправки менеджеру:", e)

@router.message()
async def manager_reply(message: Message):
    user_id = message.from_user.id
    if user_id in MANAGER_IDS and user_id in awaiting_reply:
        original_user_id = awaiting_reply.pop(user_id)
        try:
            await bot.send_message(original_user_id, f"💬 Ответ от специалиста:\n\n{message.text or '[медиа]'}")
            await message.answer("✅ Ответ отправлен.")
        except:
            await message.answer("❌ Не удалось отправить (пользователь ушёл).")

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
TELEGRAM_TOKEN = "your-telegram-token-here"
OPENAI_API_KEY = "your-openai-api-key-here"

ADMINS = [621587126, 619318985]  # @kazakoff_kalyamba, @anka_miron

bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# ——— Фильтр: не реагировать на одни эмодзи/реакции
REACTIONS = ["🔥", "❤️", "😂", "😍", "😢", "👏", "😮"]

def is_valid_message(message: types.Message) -> bool:
    return message.text and message.text.strip() not in REACTIONS

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! 👋 Напиши мне, если хочешь узнать что-то о наших товарах, сделать заказ или просто пообщаться. Я постараюсь помочь по максимуму 😊")

@dp.message(F.text)
async def handle_message(message: Message):
    if not is_valid_message(message):
        return

    user_msg = message.text.strip()

    try:
        system_prompt = (
            "Ты — дружелюбный, стильный и немного дерзкий чат-бот от имени WHY NOT Wakeboard. "
            "Общайся на русском, английском или французском, как клиент. Говори с юмором, дружелюбно, живо. "
            "Поддерживай, если клиент прислал фейл. Отвечай на заказы, вопросы, сленг и кэмпы как будто ты их райдер-друг."
        )

        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.85
        )
        reply = response.choices[0].message.content.strip()

        await message.answer(reply)

        # отправка админу
        for admin in ADMINS:
            await bot.send_message(
                chat_id=admin,
                text=(
                    f"<b>💬 Вопрос от @{message.from_user.username or message.from_user.first_name}:</b>\n"
                    f"{user_msg}\n\n"
                    f"<b>🤖 Ответ:</b>\n{reply}"
                )
            )

    except Exception as e:
        logging.exception("Ошибка при генерации ответа")
        await message.answer("Упс, что-то пошло не так! Попробуй позже 🛠")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import asyncio
    asyncio.run(dp.start_polling(bot))

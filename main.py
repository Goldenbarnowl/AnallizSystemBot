import asyncio
import json
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.types import PollAnswer
from aiogram.filters import Command

# Загрузка вопросов из JSON-файла
with open("questions_with_answers.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

# Инициализация бота
API_TOKEN = ""
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_quiz(message: types.Message, state: FSMContext):
    poll = await bot.send_poll(
        chat_id=message.chat.id,
        question="[1/211] "+questions[0]["question"],
        options=questions[0]["options"],
        allows_multiple_answers=True,
        is_anonymous=False
    )
    await state.update_data(stage="0")


@dp.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer, state: FSMContext):
    user_id = poll_answer.user.id
    data = await state.get_data()
    stage = int(data.get("stage"))

    # Ответы пользователя (индексы)
    user_answers = poll_answer.option_ids

    # Преобразование индексов в текстовые варианты
    user_selected_options = [questions[stage]["options"][i][:2].strip() for i in user_answers]

    # Проверка, что все правильные ответы выбраны
    correct_answers_set = questions[stage]["correct_answers"]

    is_all_correct = correct_answers_set == user_selected_options

    if is_all_correct:
        await bot.send_message(user_id, "✅ Все верно!")
    else:
        await bot.send_message(user_id, "❌ Неправильные ответы: " + ", ".join(user_selected_options) + "\nПравильные ответы: " + ", ".join(correct_answers_set))
    stage += 1
    await state.update_data(stage=str(stage))

    await bot.send_poll(
        chat_id=user_id,
        question=f"[{stage+1}/211] "+questions[stage]["question"],
        options=questions[stage]["options"],
        allows_multiple_answers=True,
        is_anonymous=False
    )


async def start():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(start())

from config import *
import tools

import asyncio
import logging
import sys

from aiogram import Bot, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import Message, ChatMemberUpdated, CallbackQuery, LinkPreviewOptions
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.formatting import Text, ExpandableBlockQuote, Bold
from aiogram.fsm.context import FSMContext

dialog_mode = False


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Привет! Просто задай свой вопрос, а я попробую тебе помочь.")


@dp.message(Command("refresh"))
async def command_refresh_handler(message: Message) -> None:
    await tools.refresh()
    await message.answer("Актуальные данные скачаны из таблицы!")


@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated, bot: Bot):
    await asyncio.sleep(1)
    await bot.send_chat_action(event.chat.id, action="typing")
    await asyncio.sleep(4)
    await event.answer("Привет! Ты новенький, представься)")


@dp.message(Command("summarize"))
async def command_summarize_handler(message: Message) -> None:
    if str(message.chat.id) == UNDERGROUND_CHAT_ID:
        text_to_summarize = await tools.context_to_text()
        summary = await tools.summarize(text_to_summarize)
        await message.reply(summary)


@dp.message(Command("dialog"))
async def command_dialog_handler(message: Message) -> None:
    global dialog_mode

    if str(message.chat.id) == UNDERGROUND_CHAT_ID and DIALOG_MODE_ON:
        dialog_mode = not dialog_mode

        await message.reply('Ура, теперь я полноценный участник беседы!' if dialog_mode else 'Всем пока!')


@dp.message()
async def chat_message_handler(message: Message, state: FSMContext) -> None:
    global dialog_mode

    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        if await tools.mentioned(message.text):
            reply = await tools.formatted_reply(message.text,
                                                message.quote.text,
                                                message.from_user.first_name,
                                                dialog_mode)
            await message.reply(reply)
            await tools.update_undergound_context(reply, "Артем Макаров")

        if "&&" in message.text and await tools.is_admin(message):
            keywords = message.text.replace("&& ", "").replace("&&", "")
            answer = message.reply_to_message.text
            await tools.add_new_question(keywords, answer)
            await tools.refresh()
            await message.reply("Добавлено!")

        if message.text == "!а" and message.text == "!a":
            question = message.reply_to_message.text
            author = message.reply_to_message.from_user.first_name

            reply = await tools.formatted_reply(question, author=author)

            await message.reply_to_message.reply(reply)
            await tools.update_undergound_context(reply, "Артем Макаров")
    else:
        reply = await tools.formatted_reply(message.text)
        await message.reply(reply)
        await tools.update_undergound_context(reply, "Артем Макаров")
        await state.update_data({"text":message.text})

    await tools.update_undergound_context(message)


@dp.callback_query(F.data == "ASK")
async def handle_answer_quality(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    data = await state.get_data()

    text = data["text"]

    message = Text(
        Bold("Кураторы!\n\nАноним задает вопрос:\n"),
        ExpandableBlockQuote(text))

    await bot.send_message(UNDERGROUND_CHAT_ID, **message.as_kwargs())
    await callback.message.edit_text(
        f"Твой вопрос отправлен!\n Жди ответа в чате по [ссылке]({UNDERGROUND_CHAT_INVITE}).",
        parse_mode=ParseMode.MARKDOWN, link_preview_options=LinkPreviewOptions(is_disabled=True))

    await state.clear()


@dp.callback_query(F.data == "OK")
async def idle_handler(state: FSMContext) -> None:
    await state.clear()


# @dp.error(TelegramNetworkError)
# async def on_network_error(error: TelegramNetworkError) -> None:
#     await error.method.


async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await tools.refresh()
    await dp.start_polling(bot, polling_timeout=100, )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

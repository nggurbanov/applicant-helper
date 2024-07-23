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
from aiogram.exceptions import TelegramNetworkError

# bot global vars

dialog_mode = False


# aiogram tools

async def is_admin(message: Message) -> bool:
    return message.from_user.username in ADMINS


def get_reply_history(message: Message, length: int = 25) -> list[str]:
    count = 0
    history = []

    current_message = message.reply_to_message

    while current_message is not None and count < length:
        history.append(f'{current_message.from_user.first_name}: {current_message.text}')

        current_message = current_message.reply_to_message

        count += 1

    return history[::-1]


# aiogram event handlers

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
    if message.chat.id == UNDERGROUND_CHAT_ID:
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

    if message.chat.id != UNDERGROUND_CHAT_ID:
        return

    await tools.update_underground_context(message.text, name=message.from_user.first_name)

    is_answer = (message.reply_to_message is not None
                 and message.reply_to_message.from_user.is_bot
                 and REPLY_ON_REPLY)

    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        if await tools.mentioned(message.text) or is_answer:
            reply = await tools.formatted_reply(message.text,
                                                get_reply_history(message) if REPLIES_CONTEXT else [],
                                                message.from_user.first_name,
                                                dialog_mode)
            await message.reply(reply)
            await tools.update_underground_context(reply, "Артем Макаров")

        if "&&" in message.text and await is_admin(message):
            keywords = message.text.replace("&& ", "").replace("&&", "")
            answer = message.reply_to_message.text
            await tools.add_new_question(keywords, answer)
            await tools.refresh()
            await message.reply("Добавлено!")

        if message.text == "!а" and message.text == "!a":
            question = message.reply_to_message.text
            author = message.reply_to_message.from_user.first_name
            quote = message.reply_to_message.quote.text

            reply = await tools.formatted_reply(question, replies=[quote], author=author)

            await message.reply_to_message.reply(reply)
            await tools.update_underground_context(reply, "Артем Макаров")
    else:
        reply = await tools.formatted_reply(message.text)

        await message.reply(reply)
        await tools.update_underground_context(reply, "Артем Макаров")
        await state.update_data({"text":message.text})


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


@dp.error(TelegramNetworkError)
async def on_network_error(error: TelegramNetworkError) -> None:
    # await error.message.reply("Произошла ошибка. Попробуйте еще раз.") # i think it is not work

    print(error.message)


async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await tools.refresh()
    await dp.start_polling(bot, polling_timeout=100)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

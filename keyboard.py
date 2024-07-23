from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Мне помог ответ, спасибо!", callback_data="OK"),
        ],
        [
            InlineKeyboardButton(text="Анонимно спросить кураторов.", callback_data="ASK"),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard

from config import HISTORY_PROMPT, QUOTE_PROMPT, MESSAGE_PROMPT


def promt_render(promt, **kwargs) -> str:
    for key, value in kwargs.items():
        promt = promt.replace(f'{key}', value)

    return promt


def message_history_promt(history: str) -> str:
    return promt_render(HISTORY_PROMPT, history=history)


def quote_promt(text: str) -> str:
    return promt_render(QUOTE_PROMPT, quote=text)


def message_promt(text: str, author: str = 'user') -> str:
    return promt_render(MESSAGE_PROMPT, message=text, author=author)

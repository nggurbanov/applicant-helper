from config import HISTORY_PROMPT, QUOTE_PROMPT, MESSAGE_PROMPT


def message_history_promt(history: str) -> str:
    return HISTORY_PROMPT.replace('{history}', history)


def quote_promt(text: str) -> str:
    return QUOTE_PROMPT.replace('{quote}', text)


def message_promt(text: str, author: str = 'user') -> str:
    return MESSAGE_PROMPT.replace('{message}', text).replace('{author}', author)

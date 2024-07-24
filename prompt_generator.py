from config import HISTORY_PROMPT, REPLY_PROMPT, MESSAGE_PROMPT


def prompt_render(promt, **kwargs) -> str:
    for key, value in kwargs.items():
        promt = promt.replace('{' + key + '}', value)

    return promt


def message_history_prompt(history: str) -> str:
    return prompt_render(HISTORY_PROMPT, history=history)


def reply_prompt(text: str, author: str = 'user') -> str:
    return prompt_render(REPLY_PROMPT, reply=text, author=author)


def message_prompt(text: str, author: str = 'user') -> str:
    return prompt_render(MESSAGE_PROMPT, message=text, author=author)

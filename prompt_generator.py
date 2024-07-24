from config import HISTORY_PROMPT, REPLIES_PROMPT, MESSAGE_PROMPT


def prompt_render(promt, **kwargs) -> str:
    for key, value in kwargs.items():
        promt = promt.replace('{' + key + '}', value)

    return promt


def message_history_prompt(history: str) -> str:
    return prompt_render(HISTORY_PROMPT, history=history)


def replies_prompt(text: str) -> str:
    return prompt_render(REPLIES_PROMPT, replies=text)


def message_prompt(text: str, author: str = 'user') -> str:
    return prompt_render(MESSAGE_PROMPT, message=text, author=author)

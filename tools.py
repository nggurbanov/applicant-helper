import emoji_remover

from config import *
from prompt_generator import message_history_prompt, replies_prompt, message_prompt

underground_chat_context = []


async def add_new_question(question: str, answer: str) -> None:
    worksheet.append_row([question, answer], value_input_option="RAW")


async def generate_short(message: str, replies: list = None, author: str = 'user') -> str:
    messages = [{"role":"system", "content":NON_FOUND_PROMPT},
                {"role":"user", "content":message_prompt(message, author)}]

    if replies is not None and len(replies) > 0:
        messages.insert(1, {"role":"system", "content":replies_prompt('\n'.join(replies))})

    chat_response = ai_client.chat.completions.create(
        model=ANSWER_MODEL,
        messages=messages,
        temperature=0.5
    )
    response_text = chat_response.choices[0].message.content

    return response_text


async def generate_dialog(message: str, author: str = 'user') -> str:
    messages = [{"role":"system", "content":NON_FOUND_PROMPT},
                {"role":"system", "content":message_history_prompt(context_to_text())},
                {"role":"user", "content":message_prompt(message, author)}]

    chat_response = ai_client.chat.completions.create(
        model=ANSWER_MODEL,
        messages=messages,
        temperature=0.5
    )
    response_text = chat_response.choices[0].message.content

    return response_text


async def find_question(message: str) -> str:
    current_search_prompt = SEARCH_PROMPT.format(enumerated_questions=enumerated_questions)
    messages = [{"role":"system", "content":current_search_prompt},
                {"role":"user", "content":message}]

    chat_response = ai_client.chat.completions.create(
        model=SEARCH_MODEL,
        messages=messages,
        temperature=0
    )
    response_text = chat_response.choices[0].message.content

    return response_text


def find_answer(number: int):
    return answers[number - 1]


async def refresh() -> None:
    global df, questions, answers, enumerated_questions

    questions = worksheet.col_values(1)
    answers = worksheet.col_values(2)
    enumerated_questions = '\n'.join([f"{index + 1}. {item}" for index, item in enumerate(questions)])


async def mentioned(text: str) -> bool:
    return any(mention in text.lower() for mention in MENTIONS)


async def reply(text: str, replies: list = None, author='user', dialog_mode: bool = False) -> str:
    number = int(await find_question(text))

    if number == 0:
        response = await generate_short(text, replies, author) if not dialog_mode \
            else await generate_dialog(text, author)
    else:
        response = find_answer(number)

    return response


async def remove_names(input_string: str) -> str:
    for mention in MENTIONS:
        input_string = input_string.replace(mention, '')

    return input_string


async def deepinfra_test(message: str) -> str:
    messages = [{"role":"system", "content":NON_FOUND_PROMPT}, {"role":"user", "content":message}]

    chat_response = deepinfra_client.chat.completions.create(
        model=ANSWER_MODEL,
        messages=messages,
        temperature=0
    )
    response_text = chat_response.choices[0].message.content

    return response_text


async def summarize(text: str) -> str:
    messages = [{"role":"system", "content":SUMMARIZE_PROMPT}, {"role":"user", "content":text}]

    chat_response = ai_client.chat.completions.create(
        model=ANSWER_MODEL,
        messages=messages,
        temperature=0.5
    )
    summary = chat_response.choices[0].message.content

    return summary


async def update_underground_context(message: str, name: str = None) -> None:
    global underground_chat_context

    underground_chat_context.append(name + ": " + message)

    if len(underground_chat_context) > 50:
        del underground_chat_context[0]


async def formatted_reply(text: str, replies: list = None, author: str = 'user', dialog_mode: bool = False):
    reply_msg = await reply(text, replies, author, dialog_mode)
    formatted_response = await emoji_remover.rm(reply_msg.lower())

    return formatted_response


async def context_to_text(length: int = 20) -> str:
    text_to_summarize = "\n".join(underground_chat_context[:length + 1])

    return text_to_summarize

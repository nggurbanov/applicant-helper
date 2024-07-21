from config import *
import emoji_remover

underground_chat_context = []

async def add_new_question(question, answer):
    worksheet.append_row([question, answer], value_input_option="RAW")

async def generate_short(message):
        messages = [{"role":"system", "content":NON_FOUND_PROMPT},{"role":"user", "content":message}]

        chat_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.5
        )
        response_text = chat_response.choices[0].message.content

        return response_text

async def find_question(message):   
    messages = [{"role":"system", "content":SEARCH_PROMPT},{"role":"user", "content":message}]

    chat_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0
        )
    response_text = chat_response.choices[0].message.content

    return response_text

def find_answer(number):
    return answers[number-1]

async def refresh():
    global df, questions, answers, enumerated_questions
    questions = worksheet.col_values(1)
    answers = worksheet.col_values(2)
    enumerated_questions = '\n'.join([f"{index + 1}. {item}" for index, item in enumerate(questions)])

async def mentioned(text):
    if any(mention in text.lower() for mention in MENTIONS):
        return True

async def reply(text):
        number = int(await find_question(text))
        if number == 0:
            response = await generate_short(text)
        else:
            response = find_answer(number)
        return response

async def remove_names(input_string):
    for mention in MENTIONS:
        input_string = input_string.replace(mention, '')

    return input_string

async def deepinfra_test(message):
        messages = [{"role":"system", "content":NON_FOUND_PROMPT},{"role":"user", "content":message}]

        chat_response = deepinfra_client.chat.completions.create(
            model=ANSWER_MODEL,
            messages=messages,
            temperature=0
        )
        response_text = chat_response.choices[0].message.content

        return response_text

async def summarize(text):
    messages = [{"role":"system", "content":SUMMARIZE_PROMPT},{"role":"user", "content":text}]

    chat_response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5
    )
    summary = chat_response.choices[0].message.content

    return summary

async def update_undergound_context(message, name: None):
    global undergound_chat_context
    if str(message.chat.id) == UNDERGROUND_CHAT_ID:
        if not name:
            underground_chat_context.append(message.from_user.first_name + ": " + message.text)
        else:
            underground_chat_context.append(name + ": " + message)
        if len(underground_chat_context) > 50:
            del underground_chat_context[0]

async def formatted_reply(text):
    reply = await reply(text)
    formatted_response = await emoji_remover.rm(reply.lower())
    return formatted_response

async def is_admin(message):
    if message.from_user.username in ADMINS:
        return True
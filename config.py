from aiogram import Dispatcher

from aiogram.fsm.state import State
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
import os
import json
import openai
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

# flags
DIALOG_MODE_ON = False
REPLY_CONTEXT = True
REPLY_ON_REPLY = True

load_dotenv()

DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")  # optional
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI = True if OPENAI_API_KEY else False

# optional, for open-source model use with Deepinfra
SEARCH_MODEL = os.getenv("SEARCH_MODEL") if not OPENAI else 'gpt-4o-mini'
ANSWER_MODEL = os.getenv("ANSWER_MODEL") if not OPENAI else 'gpt-4o-mini'

# load some config data
with open("./underground_info/group_chat.json", encoding='utf-8-sig') as file:
    underground_data = json.load(file)

UNDERGROUND_CHAT_ID = int(underground_data.get("CHAT_ID"))
UNDERGROUND_CHAT_INVITE = underground_data.get("CHAT_INVITE")

with open("./underground_info/admins.json") as file:
    ADMINS = json.load(file)

with open("./gspread_handler/url.txt") as file:
    SHEET_URL = file.read().strip()

# load prompts
with open("./prompts/non-found.txt", encoding='utf-8-sig') as file:
    NON_FOUND_PROMPT = file.read()

with open("./prompts/search.txt", encoding='utf-8-sig') as file:
    SEARCH_PROMPT = file.read()

with open("./prompts/summarize.txt", encoding='utf-8-sig') as file:
    SUMMARIZE_PROMPT = file.read()

with open("./prompts/history.txt", encoding='utf-8-sig') as file:
    HISTORY_PROMPT = file.read()

with open("prompts/reply.txt", encoding='utf-8-sig') as file:
    REPLY_PROMPT = file.read()

with open("./prompts/message.txt", encoding='utf-8-sig') as file:
    MESSAGE_PROMPT = file.read()

with open("./prompts/filter.txt", encoding='utf-8-sig') as file:
    FILTER_PROMPT = file.read()

with open("./prompts/stay_active.txt", encoding='utf-8-sig') as file:
    STAY_ACTIVE_PROMPT = file.read()

with open("./prompts/stay_active_no_context.txt", encoding='utf-8-sig') as file:
    STAY_ACTIVE_NC_PROMPT = file.read()

# some google worksheet
scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file('./gspread_handler/key.json', scopes=scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_url(SHEET_URL)
worksheet = spreadsheet.sheet1

# load mentions
with open("./underground_info/mentions.json", "r", encoding='utf-8-sig') as file:
    MENTIONS = json.load(file)

# init ai clients
deepinfra_client = openai.OpenAI(
    api_key=DEEPINFRA_API_KEY,
    base_url="https://api.deepinfra.com/v1/openai")

ai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI else deepinfra_client

# save token
TOKEN = os.getenv("BOT_TOKEN")

# init dispatcher
dp = Dispatcher()
dp.callback_query.middleware(CallbackAnswerMiddleware(pre=True))

text_state = State()

BOSS_ID=int(os.getenv("BOSS_ID"))
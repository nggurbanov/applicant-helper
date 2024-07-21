import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramNetworkError
from aiogram.dispatcher.middlewares.base import BaseMiddleware

API_TOKEN = 'YOUR_BOT_API_TOKEN'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

class RetryMiddleware(BaseMiddleware):
    def __init__(self, retries=3, delay=5):
        self.retries = retries
        self.delay = delay
        super(RetryMiddleware, self).__init__()

    async def on_pre_process_message(self, message: types.Message, data: dict):
        for attempt in range(self.retries):
            try:
                return await self.on_process_message(message, data)
            except TelegramNetworkError as e:
                if attempt < self.retries - 1:
                    await asyncio.sleep(self.delay)
                else:
                    raise e

    async def on_process_message(self, message: types.Message, data: dict):
        # This method will be overridden by the actual handler
        pass



if __name__ == '__main__':
    from aiogram import executor
    dp.middleware.setup(RetryMiddleware())
    executor.start_polling(dp, skip_updates=True)
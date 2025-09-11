from telegram import Bot
import asyncio
from dotenv import load_dotenv
load_dotenv()
import os

class BotSender:
    def __init__(self):
        self.token = os.getenv('ERROR_BOT_TOKEN')
        self.chat_id = os.getenv('TG_USER_ADMIN')

    async def send_notification_async(self, message):
        try:
            bot = Bot(token=self.token)
            await bot.send_message(chat_id=self.chat_id, text=message)
            print("Сообщение отправлено в Telegram")
        except Exception as e:
            print(f"Ошибка отправки: {e}")

    def send_notification(self, message):
        """Синхронная версия для крона"""
        asyncio.run(self.send_notification_async(message))
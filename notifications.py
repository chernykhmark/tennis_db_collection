from telegram import Bot
import asyncio


class BotSender:
    def __init__(self):
        self.token = '8204765665:AAGXEvVwahAMjQisRxqk4x1QtUDhwDpEyLY'
        self.chat_id = '1030144895'

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
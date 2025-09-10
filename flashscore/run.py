import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eurosport.driver import driver_get_flashscore
from datetime import datetime
from eurosport.notifications import BotSender

URL = 'https://www.flashscore.co.uk/tennis/'

def main():
    print(f"\n{'=' * 60}\n")
    global URL
    bot = BotSender()
    try:
        os.makedirs('data', exist_ok=True)
        driver_get_flashscore(URL)
    except Exception as e:
        error_msg = f"[{datetime.now()}] Ошибка в скрипте: {str(e)}"
        bot.send_notification(error_msg)

if __name__=='__main__':
    main()

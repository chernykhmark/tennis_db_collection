from driver import driver_get_tommorow_page_source
from shedule import get_daily_schedule
from database import Database
from datetime import datetime,timedelta
import pytz
from notifications import BotSender

URL = 'https://www.eurosport.com/tennis/score-center.shtml'
day = datetime.now(pytz.timezone('Europe/Moscow'))  # укажи свой часовой пояс
tomorrow = day + timedelta(days=1)
tomorrow_date = tomorrow.strftime('%Y-%m-%d')

def main():
    global URL,tomorrow_date
    db = Database()
    bot = BotSender()
    try:
        tomorrow_page_source = driver_get_tommorow_page_source(URL)
        get_daily_schedule(tomorrow_page_source,db,tomorrow_date)

    except Exception as e:
        error_msg = f"[{datetime.now()}] Ошибка в скрипте: {str(e)}"
        bot.send_notification(error_msg)

    finally:
        db.close()

if __name__=='__main__':
    main()

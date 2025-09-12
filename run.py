from driver import driver_get_page_source
from shedule import get_daily_schedule
from database import Database
from notifications import BotSender
from  datetime import datetime

URL = 'https://www.eurosport.com/tennis/score-center.shtml'

def main():
    print(f"\n{'=' * 60}\n")
    global URL
    bot = BotSender()
    db = Database()
    try:
        page_source = driver_get_page_source(URL)
        get_daily_schedule(page_source,db)
        db.update_all_null_winners()

    except Exception as e:
        error_msg = f"[{datetime.now()}] Ошибка в скрипте: {str(e)}"
        bot.send_notification(error_msg)

    finally:
        db.close()

if __name__=='__main__':
    main()

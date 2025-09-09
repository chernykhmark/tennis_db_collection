from driver import get_chrome_driver, driver_get_page_source, driver_get_tommorow_page_source
from shedule import get_daily_schedule
from database import Database
from datetime import datetime,timedelta
import pytz

URL = 'https://www.eurosport.com/tennis/score-center.shtml'
day = datetime.now(pytz.timezone('Europe/Moscow'))  # укажи свой часовой пояс
tomorrow = day + timedelta(days=1)
tomorrow_date = tomorrow.strftime('%Y-%m-%d')

def main():
    global URL,tomorrow_date
    db = Database()
    driver = get_chrome_driver()
    tomorrow_page_source = driver_get_tommorow_page_source(driver, URL)

    get_daily_schedule(tomorrow_page_source,db,tomorrow_date)
    driver.quit()
    db.close()

if __name__=='__main__':
    main()

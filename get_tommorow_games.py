from driver import get_chrome_driver, driver_get_page_source, driver_get_tommorow_page_source
from shedule import get_daily_schedule
from database import Database

URL = 'https://www.eurosport.com/tennis/score-center.shtml'

def main():
    global URL
    db = Database()
    driver = get_chrome_driver()
    tomorrow_page_source,dt = driver_get_tommorow_page_source(driver, URL)
    get_daily_schedule(tomorrow_page_source,db,dt)
    driver.quit()
    db.close()

if __name__=='__main__':
    main()

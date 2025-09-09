from driver import get_chrome_driver, driver_get_page_source, update_chrome_driver
from shedule import get_daily_schedule
from database import Database

URL = 'https://www.eurosport.com/tennis/score-center.shtml'

def main():
    global URL
    db = Database()
    driver = get_chrome_driver()
    page_source,dt = driver_get_page_source(driver, URL)
    get_daily_schedule(page_source,db,dt)
    driver.quit()
    print('Driver stop')
    db.update_all_null_winners()
    db.close()

if __name__=='__main__':
    main()

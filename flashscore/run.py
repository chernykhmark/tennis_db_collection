from driver import driver_get_flashscore


URL = 'https://www.flashscore.co.uk/tennis/'

def main():
    global URL
    driver_get_flashscore(URL)

if __name__=='__main__':
    main()

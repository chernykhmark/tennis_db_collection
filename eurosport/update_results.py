import time as t
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import random

def get_random_headers():
    # Инициализация UserAgent
    ua = UserAgent()
    # Случайный User-Agent
    user_agent = ua.random
    # Другие заголовки для сокрытия автоматизации
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',  # Do Not Track
    }

    return headers

def request_and_parse(url, proxies=None):
    # Случайная задержка от 1 до 5 секунд перед запросом
    t.sleep(random.uniform(1, 5))
    # Генерация случайных заголовков
    headers = get_random_headers()
    # Дополнительно можно использовать список прокси-серверов
    if proxies:
        proxy = random.choice(proxies)
        response = requests.get(url, headers=headers, proxies={'http': proxy, 'https': proxy})
    else:
        response = requests.get(url, headers=headers)
    # Проверка на успешный запрос
    if response.status_code == 200:
        # Передача ответа в BeautifulSoup для парсинга
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        print(f"Ошибка: {response.status_code}")
        return None

def get_results(URL):
    soup = request_and_parse(URL)
    if soup == None:
        winner = 'untouch link'
        return winner
    match_header_content = soup.find('div',{'data-testid':'atom-set-match-header-content'})
    player_divs = match_header_content.find_all('div', class_='flex min-h-[25px] lg:min-h-8')
    
    player_one = player_divs[0]
    bye_winner_one = player_one.get_text(strip=True)
    player_two = player_divs[1]
    bye_winner_two = player_two.get_text(strip=True)
    
    if bye_winner_one == 'BYE':
        try:
            bye_winner_two = bye_winner_two.split(' (')[0]
        except:
            pass
        return bye_winner_two
    elif bye_winner_two == 'BYE':
        try:
            bye_winner_one = bye_winner_one.split(' (')[0]
        except:
            pass
        return bye_winner_one

    try:
        winner_icon_one = player_one.find('svg', {'data-testid': 'vertical-head-to-head-score-atom-winner-home-icon'})
        if winner_icon_one:
            winner = player_one.get_text(strip=True)
            try:
                winner = winner.split(' (')[0]
            except:
                pass
            return winner
    except:
        pass
    try:
        winner_icon_two = player_two.find('svg', {'data-testid': 'vertical-head-to-head-score-atom-winner-away-icon'})
        if winner_icon_two:
            winner = player_two.get_text(strip=True)
            try:
                winner = winner.split(' (')[0]
            except:
                pass
            return winner
    except:
        pass




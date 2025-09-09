from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from update_results import request_and_parse

def get_player_rank(href,game_id):
    soup = request_and_parse(href)

    main_table = soup.find('div', {'data-testid':"match-tab-main-column"})
    persons_cards =main_table.find('div',{'data-testid':"organism-match-persons-cards"})
    try:
        persons_cards_list =persons_cards.find_all('div',class_="w-1/2")
    except:
        player_one_rank = 0
        player_two_rank = 0
        print(f'exception with get_player_rank from persons_cards for {game_id}')
        return player_one_rank, player_two_rank
    value_list = []
    for card in persons_cards_list:
        player_card = card.find('div',{'data-testid':"atom-characteristics-card"})
        values = player_card.find_all('span',{'data-testid':"atom-characteristics-competition-value"})
        for val in values:
            value_list.append(val.text)

    one_rank = value_list[0]
    two_rank = value_list[2]

    try:
        player_one_rank = int(one_rank)
    except:
        player_one_rank = 0

    try:
        player_two_rank = int(two_rank)
    except:
        player_two_rank = 0

    return player_one_rank, player_two_rank

def h2h_players_wins(soup):
    try:
        h2h_info_div = soup.find('div',{'data-testid':'organism-match-head-to-head-matches'})
        # НАЙТИ ПОБЕДЫ В ЛИЧНЫХ ВСТРЕЧАХ
        h2h_score = h2h_info_div.find('div', class_="mt-2 lg:mt-3")
        h2h_scores = h2h_score.find_all('div',{'data-testid' : 'match-statistics-main-row-value'})
        values = [int(element.get_text(strip=True)) for element in h2h_scores]
        #Победа первого и второго (число)
        h2h_player_one_wins = values[0]
        h2h_player_two_wins = values[1]
    except:
        h2h_player_one_wins = 0
        h2h_player_two_wins = 0

    return h2h_player_one_wins, h2h_player_two_wins


def last_five_games_by_player(soup):
    def remove_sup_tags(soup):
        for sup_tag in soup.find_all('sup'):
            sup_tag.decompose()
        return soup

    soup = remove_sup_tags(soup)

    player_name = soup.find('p', {'data-testid': 'previous-participant-matches-name'}).text.strip()
    # Шаг 2: Подсчет количества побед
    try:
        previous_matches_wins = len(soup.find_all('svg', {'data-testid': 'previous-participant-matches-icon-win'}))
    except:
        previous_matches_wins = 0
    # Шаг 3: Подсчет количества цифр "7" в зависимости от позиции игрока в каждом матче
    try:
        matches = soup.find_all('div', {'data-testid': 'organism-match-card'})

        sevens_count = 0

        for match in matches:
            player_home = match.find('div',
                                     {'data-testid': 'vertical-head-to-head-score-atom-player-home-content-box'}).text
            player_away = match.find('div',
                                     {'data-testid': 'vertical-head-to-head-score-atom-player-away-content-box'}).text

            div_elements = match.find_all('div', {'class': 'truncate px-0.75 leading-16'})

            # Извлечение текста только из основного div, исключая вложенные элементы
            all_digits = []
            for div in div_elements:
                main_text = ''.join(div.find_all(string=True, recursive=False)).strip()
                all_digits.extend(main_text)

            # Разделение списка на две части
            mid_index = len(all_digits) // 2
            first_half = all_digits[:mid_index]
            second_half = all_digits[mid_index:]
            # Если игрок на домашней позиции
            if player_name in player_home:
                sevens_count += first_half.count('7')
            # Если игрок на выездной позиции
            elif player_name in player_away:
                sevens_count += second_half.count('7')
    except:
        sevens_count = 0

    return previous_matches_wins, sevens_count

def compare_players(player_one, player_one_rank, h2h_player_one_wins, prev_match_player_one_wins, prev_match_player_one_sevens_count,
                    player_two, player_two_rank, h2h_player_two_wins, prev_match_player_two_wins, prev_match_player_two_sevens_count):
    # Начальные баллы игроков
    player_one_score = 0
    player_two_score = 0

                # Исключаем строки с 'BYE' и 'Не определен'
    if 'BYE' in (player_one, player_two):
        winner = player_one if player_two == 'BYE' else player_two
        return winner, 0
    # Сравнение по рангу: меньше ранг - больше баллов
    if player_one_rank != 0 and player_two_rank != 0 and abs(player_one_rank - player_two_rank) < 5:
    # Разница рейтингов меньше 5, очки не добавляются
        pass
    else:
        if player_one_rank != 0 and (player_one_rank < player_two_rank or player_two_rank == 0):
            player_one_score += 1
        elif player_two_rank != 0 and (player_two_rank < player_one_rank or player_one_rank == 0):
            player_two_score += 1

    # Сравнение количества побед в личных встречах
    if h2h_player_one_wins > h2h_player_two_wins:
        player_one_score += 1
    elif h2h_player_two_wins > h2h_player_one_wins:
        player_two_score += 1

    # Сравнение количества побед в последних пяти матчах
    if prev_match_player_one_wins > prev_match_player_two_wins:
        player_one_score += 1
    elif prev_match_player_two_wins > prev_match_player_one_wins:
        player_two_score += 1

    # Сравнение количества набранных очков
    if prev_match_player_one_sevens_count > prev_match_player_two_sevens_count:
        player_one_score += 1
    elif prev_match_player_two_sevens_count > prev_match_player_one_sevens_count:
        player_two_score += 1

    # Определение победителя и разницы в баллах
    if player_one_score > player_two_score:
        return player_one, player_one_score - player_two_score
    elif player_two_score > player_one_score:
        return player_two, player_two_score - player_one_score
    else:
        return "Не определен", 0


def get_daily_schedule(page_source,db,dt):

    def extract_player_info(elem):
        text = elem.get_text(strip=True)
        try:
            name = text.split(' (')[0]
        except ValueError:
            # Если ранг отсутствует, установить как 0
            name = text
        return name


    soup = BeautifulSoup(page_source, 'html.parser')

    if dt == 'None':
        print('!dt nonetype')
        dt = pd.Timestamp.now().strftime('%Y-%m-%d')

    try:
        games_list = soup.find_all('a', {'data-testid': "link-match-card"})
    except:
        return

    try:
        href_list = [link.get('href') for link in games_list if
                     'tennis' in link.get('href') and 'doubles' not in link.get('href')]
    except:
        return

    # Переводим href_list в множество для быстрого поиска
    href_set = set(href_list)
    # Отфильтровываем links_list по href
    filtered_game_list = [link for link in games_list if link.get('href') in href_set]
    if len(filtered_game_list) == 0:
        return

    for game in tqdm(filtered_game_list):

        player_one_elem = game.find('div', {'data-testid': 'vertical-head-to-head-score-atom-player-home-content-box'})
        player_two_elem = game.find('div', {'data-testid': 'vertical-head-to-head-score-atom-player-away-content-box'})

        player_one = extract_player_info(player_one_elem)
        player_two = extract_player_info(player_two_elem)

        if player_one == '' or player_two == '':
            continue
        href = game.get('href')

        sett = href.split('/')
        tourner = sett[4]
        game_id = sett[6].split('_')[1]

        if db.check_game_id_exists(game_id):
            continue

        try:
            time = game.find('div', {'data-testid': "vertical-head-to-head-score-atom-no-score-content-box"}).text.strip().split(' ')[1]
        except:
            time = 'TBC'

        link = href.replace('.shtml', '-stats.shtml')

        player_one_rank, player_two_rank = get_player_rank(href,game_id)
        # ПЕРЕХОДИМ ПО ССЫЛКЕ И ЗАБИРАЕМ

        soup = request_and_parse(link)

        #Получаем ПОЛ и РАУНД
        soup_header = soup.find('div', {'data-testid': "organism-match-header"})
        # Проверяем, найден ли элемент
        if soup_header:
            # Ищем вложенный div по классу и извлекаем текст, если найден
            try:
                response_text_div = soup_header.find('div', class_="caps-s7-rs uppercase text-br-2-70")
                sex_round = response_text_div.get_text()
            except:
                response_text_div = soup_header.find('div',
                                                     class_="caption-2 md:caption:3 lg:caption-1 text-neutral-05")
                sex_round = response_text_div.get_text()

            sex = sex_round.split('|')[0].strip()
            rounds = sex_round.split('|')[1].strip()
        else:
            sex = ''
            rounds = ''
            print('no text!')

        # ПОБЕДЫ В ЛИЧНЫХ ВСТРЕЧАХ
        h2h_player_one_wins, h2h_player_two_wins = h2h_players_wins(soup)

        # РЕЗУЛЬТАТЫ ПОСЛЕДНИХ ИГР
        try:
            previous_matches = soup.find('div', {'data-testid': 'organism-match-previous-matches'})

            pv_first_player = \
            previous_matches.find_all('div', {'data-testid': 'molecule-match-previous-matches-participant'})[
                0]
            prev_match_player_one_wins, prev_match_player_one_sevens_count = last_five_games_by_player(pv_first_player)

            pv_second_player = \
            previous_matches.find_all('div', {'data-testid': 'molecule-match-previous-matches-participant'})[
                1]
            prev_match_player_two_wins, prev_match_player_two_sevens_count = last_five_games_by_player(pv_second_player)
        except:
            prev_match_player_one_wins = 0
            prev_match_player_one_sevens_count = 0
            prev_match_player_two_wins = 0
            prev_match_player_two_sevens_count = 0

        adv_player_name, compare_score =  compare_players(player_one, player_one_rank, h2h_player_one_wins, prev_match_player_one_wins, prev_match_player_one_sevens_count, player_two, player_two_rank, h2h_player_two_wins, prev_match_player_two_wins, prev_match_player_two_sevens_count)

        datarow = {
            'date': dt,
            'tour': tourner,
            'sex': sex,
            'round': rounds,
            'game_id': game_id,
            'adv_player_name': adv_player_name,
            'compare_score': compare_score,
            'player_one': player_one,
            'player_one_rank': player_one_rank,
            'h2h_player_one_wins': h2h_player_one_wins,
            'prev_match_player_one_wins': prev_match_player_one_wins,
            'prev_match_player_one_sevens_count': prev_match_player_one_sevens_count,
            'player_two': player_two,
            'player_two_rank': player_two_rank,
            'h2h_player_two_wins': h2h_player_two_wins,
            'prev_match_player_two_wins':prev_match_player_two_wins,
            'prev_match_player_two_sevens_count':prev_match_player_two_sevens_count,
            'link': link,
            'time': time
        }

        db.add_data(datarow)





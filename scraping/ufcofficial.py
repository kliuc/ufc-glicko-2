import requests
from bs4 import BeautifulSoup


def get_fighters(status='active'):
    if status == 'active':
        url = 'https://www.ufc.com/athletes/all?filters%5B0%5D=status%3A23&page='
    elif status == 'all':
        url = 'https://www.ufc.com/athletes/all?page='

    all_fighters = []
    page_num = 1
    while page_num <= 1000:
        response = requests.get(url + str(page_num))
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find('div', class_='ufc-search-no-results'):
            break
        fighter_cards = soup.find_all('li', class_='l-flex__item')
        fighters = [
            {'name': fighter.find('span', class_='c-listing-athlete__name').text.strip(),
             'weight_class': fighter.find('span', class_='c-listing-athlete__title').text.strip(),
             'record': fighter.find('span', class_='c-listing-athlete__record').text.strip()}
            for fighter in fighter_cards
            if fighter.find('span', class_='c-listing-athlete__name')
        ]
        all_fighters.extend(fighters)
        page_num += 1

    return all_fighters

def get_ranking(weight_class):
    response = requests.get('https://www.ufc.com/rankings')
    soup = BeautifulSoup(response.text, 'html.parser')
    rankings = soup.find_all('div', class_='view-grouping')
    ranking = next(div for div in rankings
                   if weight_class.lower() == div.find('h4').text.replace('Top Rank', '').strip().lower())
    return [row.find_all('td')[1].text.strip() for row in ranking.find_all('tr')]
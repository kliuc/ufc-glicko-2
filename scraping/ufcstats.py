import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


def get_completed_events(latest_n=None):
    response = requests.get('http://ufcstats.com/statistics/events/completed?page=all')
    soup = BeautifulSoup(response.text, 'html.parser')
    events_table = soup.find('table')
    events = events_table.find_all('i')[1:]

    all_fights = []
    for event in events[:latest_n]:
        date_text = event.find('span').text.strip()
        date = datetime.strptime(date_text, '%B %d, %Y')
        a = event.find('a')
        name = a.text.strip()
        href = a['href']
        response = requests.get(href)
        soup = BeautifulSoup(response.text, 'html.parser')
        fights_table = soup.find('tbody')
        for fight in fights_table.find_all('tr'):
            columns = fight.find_all('td')
            fight_data = {'event': name,
                          'date': date,
                          'fighter': columns[1].find_all('p')[0].text.strip(),
                          'opposition': columns[1].find_all('p')[1].text.strip(),
                          'weight_class': columns[6].text.strip(),
                          'outcome': columns[0].find('p').text.strip(),
                          'method': columns[7].find('p').text.strip()}
            all_fights.append(fight_data)

    return all_fights


if __name__ == '__main__':

    fights = pd.DataFrame(get_completed_events())
    print(fights.head(10))
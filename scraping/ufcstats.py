import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_completed_fights(latest_n_events=None):
    n = latest_n_events+1 if latest_n_events else None

    response = requests.get('http://ufcstats.com/statistics/events/completed?page=all')

    soup = BeautifulSoup(response.text, 'html.parser')
    events_table = soup.find('table')
    events = events_table.find_all('i')

    all_fights = []
    for event in events[1:n]:
        date_text = event.find('span').text.strip()
        date = datetime.strptime(date_text, '%B %d, %Y')
        a = event.find('a')
        name = a.text.strip()
        href = a['href']
        response = requests.get(href)
        soup = BeautifulSoup(response.text, 'html.parser')
        fights_table = soup.find('tbody')
        fights = [{'event': name,
                   'date': date.strftime('%Y-%m-%d'),
                   'fighter': columns[1].find_all('p')[0].text.strip(),
                   'opponent': columns[1].find_all('p')[1].text.strip(),
                   'weight_class': columns[6].text.strip(),
                   'outcome': columns[0].find('p').text.strip(),
                   'method': columns[7].find('p').text.strip()}
                   for fight in fights_table.find_all('tr')
                   for columns in [fight.find_all('td')]]
        all_fights.extend(fights)

    return all_fights


if __name__ == '__main__':

    import pandas as pd
    
    fights = pd.DataFrame(get_completed_fights(latest_n_events=5))
    print(fights.head())
    print(fights['event'].unique())
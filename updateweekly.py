"""Weekly update script to fetch new data and update ratings."""

from scraping import ufcstats
import json
import pandas as pd
from datetime import datetime
from rating.glicko2_ufc import FighterManager


# update fights.json
recent_fights = ufcstats.get_completed_fights(latest_n_events=3)
with open('data/fights.json', 'r') as f:
    fights = json.load(f)

def fight_key(fight):
    return (fight['event'], fight['fighter'], fight['opponent'])

keys = set(fight_key(fight) for fight in fights)
new_fights = [fight for fight in recent_fights if fight_key(fight) not in keys]
updated_fights = new_fights+fights
with open('data/fights.json', 'w') as f:
    json.dump(updated_fights, f)


# preprocess data (see optimization.ipynb for details)
fights_df = pd.read_json('data/fights.json').sort_values('date')
fights_df = fights_df[fights_df['date'] >= datetime(2000, 11, 17)]
fights_df = fights_df[fights_df['outcome'] != 'nc']
fights_grouped = fights_df.groupby(pd.Grouper(key='date', freq='10W'))


# calculate ratings
manager = FighterManager()
for period, group in fights_grouped:
    timestamp = period.strftime('%Y-%m-%d')
    manager.update_fighters(timestamp, group)


# update ratings.csv
ratings_df = pd.DataFrame(
    {'name': name,
     'weight_class': fighter.weight_class,
     'current_rating': fighter.rating,
     'peak_rating': fighter.peak_rating,
     'current_streak': fighter.streak,
     'best_streak': fighter.best_streak}
    for name, fighter in manager.items()
)

ratings_df.to_csv('data/ratings.csv', index=False)


# update ratings-history.json
histories = {name: fighter.history for name, fighter in manager.items()}
with open('data/rating-histories.json', 'w') as f:
    json.dump(histories, f)


# update matchups-matrix.csv
upcoming_fights = ufcstats.get_upcoming_fights()
competitors = {
    fight[fighter]
    for fight in upcoming_fights
    for fighter in ('fighter_a', 'fighter_b')
}

manager.add_fighters(competitors)
matchups_matrix = manager.get_matchups_matrix()
matchups_matrix.to_csv('data/matchups-matrix.csv', float_format='%.4f')

# update upcoming_fights.json
upcoming_fights = ufcstats.get_upcoming_fights()
with open('data/upcoming_fights.json', 'w') as f:
    json.dump(upcoming_fights, f)

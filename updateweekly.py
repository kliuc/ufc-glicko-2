from scraping import ufcstats
import json
import pandas as pd
from datetime import datetime
from glicko2_ufc import Fighter, FighterManager


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
copy_df = fights_df.copy()
copy_df[['fighter', 'opponent']] = copy_df[['opponent', 'fighter']]
copy_df['outcome'] = copy_df['outcome'].replace('win', 'loss')
fights_df = pd.concat([fights_df, copy_df], ignore_index=True)
weekly_grouped = fights_df.groupby(pd.Grouper(key='date', freq='W'))

# calculate ratings
manager = FighterManager()
for week, group in weekly_grouped:
    manager.update_fighters(group)

# update ratings.csv
ratings_df = pd.DataFrame({'name': name,
                           'current_rating': fighter.rating,
                           'peak_rating': fighter.peak_rating,
                           'current_streak': fighter.streak,
                           'best_streak': fighter.best_streak}
                           for name, fighter in manager.items())
ratings_df.sort_values('name').to_csv('data/ratings.csv')

# update ratings-history.json
histories_dict = [{'name': name, 'history': fighter.history} for name, fighter in manager.items()]
with open('data/ratings-history.json', 'w') as f:
    json.dump(histories_dict, f)
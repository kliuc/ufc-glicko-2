from scraping import ufcstats
import json

fights = ufcstats.get_completed_fights(latest_n_events=None)
with open('data/fights.json', 'w') as f:
    json.dump(fights, f)
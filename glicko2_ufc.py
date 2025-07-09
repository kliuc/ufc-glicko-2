from glicko2 import Player
import pandas as pd


class Fighter(Player):
    # this is how scoring will be determined based on fight outcome and method
    SCORING_DICT = {'win': {'KO/TKO': 1, 'SUB': 1, 'U-DEC': 1, 'M-DEC': 0.85, 'S-DEC': 0.7, 'DQ': 0.55},
                   'loss': {'KO/TKO': 0, 'SUB': 0, 'U-DEC': 0, 'M-DEC': 0.15, 'S-DEC': 0.3, 'DQ': 0.45},
                   'draw': 0.5}
    
    def __init__(self, weight_class=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weight_class = weight_class
        self.peak_rating = 0
        self.streak = self.best_streak = 0
        self.history = []
    
    def get_scores(outcomes, methods):
        return [Fighter.SCORING_DICT[outcome][method] if outcome != 'draw'
                else Fighter.SCORING_DICT['draw']
                for outcome, method in zip(outcomes, methods)]

    def update_rating(self, timestamp, opponents, outcomes, methods):
        scores = Fighter.get_scores(outcomes, methods)
        super().update_rating(opponents, scores)
        self.peak_rating = max(self.rating, self.peak_rating)
        self._update_streak(outcomes)
        self._update_history(timestamp)
    
    def _update_streak(self, outcomes):
        for outcome in outcomes:
            if outcome == 'win':
                self.streak = 1 if self.streak < 0 else self.streak + 1
                self.best_streak = max(self.streak, self.best_streak)
            elif outcome == 'loss':
                self.streak = -1 if self.streak > 0 else self.streak - 1
            elif outcome == 'draw':
                continue

    def _update_history(self, timestamp):
        lower, upper = self.get_rating_interval()
        self.history.append({'timestamp': timestamp, 'rating': self.rating, 'lower': lower, 'upper': upper})


class FighterManager(dict):
    def __init__(self, names=[], volatility=0.3001, tau=1.86):
        self._volatility = volatility
        self._tau = tau
        super().__init__({name: Fighter(volatility=self._volatility, tau=self._tau) for name in names})

    def add_fighters(self, names):
        self.update({name: Fighter(volatility=self._volatility, tau=self._tau) for name in names if name not in self})

    def update_fighters(self, timestamp, fights_df):
        # mirror fights_df, flipping 'outcome' so there are two rows for each fight (one for each fighter)
        mirrored_df = fights_df.copy()
        mirrored_df[['fighter', 'opponent']] = fights_df[['opponent', 'fighter']]
        mirrored_df['outcome'] = mirrored_df['outcome'].replace({'win': 'loss', 'loss': 'win'})
        fights_df = pd.concat([fights_df, mirrored_df], ignore_index=True)

        fights_grouped = fights_df.groupby('fighter')
        fighter_names = fights_grouped.groups.keys()
        self.add_fighters(fighter_names)
        fighters_copy = {name: self[name] for name in fighter_names}
        for name, fighter in self.items():
            if name not in fighter_names:
                fighter.did_not_compete()
            else:
                fights = fights_grouped.get_group(name)
                opponents = [fighters_copy[opponent] for opponent in fights['opponent']]
                outcomes = fights['outcome'].tolist()
                methods = fights['method'].tolist()
                fighter.update_rating(timestamp, opponents, outcomes, methods)
                
                weight_class = fights.iloc[-1]['weight_class']
                if weight_class != 'Catch Weight' and fighter.weight_class != weight_class:
                    fighter.weight_class = weight_class

from glicko2 import Player


class Fighter(Player):
    SCORING_DICT = {'win': {'KO/TKO': 1, 'SUB': 1, 'U-DEC': 1, 'M-DEC': 0.85, 'S-DEC': 0.7, 'DQ': 0.55},
                   'loss': {'KO/TKO': 0, 'SUB': 0, 'U-DEC': 0, 'M-DEC': 0.15, 'S-DEC': 0.3, 'DQ': 0.45},
                   'draw': 0.5}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.peak_rating = 0
        self.streak = 0
        self.best_streak = 0
        self.history = []
    
    def get_scores(outcomes, methods):
        return [Fighter.SCORING_DICT[outcome][method] if outcome != 'draw'
                else Fighter.SCORING_DICT['draw']
                for outcome, method in zip(outcomes, methods)]

    def update_rating(self, opponents, outcomes, methods):
        scores = Fighter.get_scores(outcomes, methods)
        super().update_rating(opponents, scores)
        self.peak_rating = max(self.rating, self.peak_rating)
        self._update_streak(outcomes)
        self._update_history()
    
    def _update_streak(self, outcomes):
        for outcome in outcomes:
            if outcome == 'win':
                self.streak = 1 if self.streak < 0 else self.streak + 1
                self.best_streak = max(self.streak, self.best_streak)
            elif outcome == 'loss':
                self.streak = -1 if self.streak > 0 else self.streak - 1
            elif outcome == 'draw':
                continue

    def _update_history(self):
        lower, upper = self.get_rating_interval()
        self.history.append({'rating': self.rating, 'lower': lower, 'upper': upper})


class FighterManager(dict):
    def __init__(self, names=[], volatility=0.06, tau=0.5):
        self._volatility = volatility
        self._tau = tau
        super().__init__({name: Fighter(volatility=self._volatility, tau=self._tau) for name in names})

    def add_fighters(self, names):
        self.update({name: Fighter(volatility=self._volatility, tau=self._tau) for name in names if name not in self})

    def update_fighters(self, fights_df):
        competitors = fights_df['fighter'].unique()
        self.add_fighters(competitors)
        manager_copy = self.copy()
        for name, fighter in self.items():
            if name not in competitors:
                fighter.did_not_compete()
            else:
                fights = fights_df[fights_df['fighter'] == name]
                opponents = [manager_copy[opponent] for opponent in fights['opponent']]
                outcomes = fights['outcome'].tolist()
                methods = fights['method'].tolist()
                fighter.update_rating(opponents, outcomes, methods)


if __name__ == '__main__':
    fighters = [Fighter() for i in range(7)]
    print(fighters[0].rating, fighters[0]._rd, fighters[0]._volatility)

    outcomes = ['win', 'win', 'draw', 'draw', 'loss', 'loss']
    methods = ['SUB', 'U-DEC', '', '', 'S-DEC', 'DQ']
    for opponent, outcome, method in zip(fighters[1:], outcomes, methods):
        print(fighters[0].p_win(opponent))
        print(fighters[0].get_rating_interval())
        fighters[0].update_rating([opponent], [outcome], [method])
        print(fighters[0].rating, fighters[0]._rd, fighters[0]._volatility)

    print(Fighter.p_a_beats_b(fighters[0], fighters[1]))
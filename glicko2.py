import numpy as np


class Player:
    TAU = 0.5

    def __init__(self, rating=1500, rd=350, volatility=0.06):
        self.rating = rating
        self._rd = rd
        self._volatility = volatility

    def update(self, oppositions, scores):
        if len(oppositions) == 0:
            self.did_not_compete()
            return
        
        v = self._v(oppositions)
        sum_gsE = self._sum_gsE(oppositions, scores)
        delta = v * sum_gsE
        self._update_volatility(delta, v)
        mu = self._mu() + self._new_rd()**2 * sum_gsE
        phi = 1 / np.sqrt(self._new_rd()**-2 + 1/v)

        self.rating =  173.7178 * mu + 1500
        self._rd =  173.7178 * phi

    def did_not_compete(self):
        phi = self._new_rd()
        self._rd = 173.7178 * phi

    def _mu(self):
        return (self.rating - 1500) / 173.7178
    
    def _phi(self):
        return self._rd / 173.7178
    
    def _g(self):
        return 1 / np.sqrt(1 + 3*self._phi()**2 / np.pi**2)
    
    def _E(self, opposition):
        g_opp = opposition._g()
        mu_opp = opposition._mu()
        return 1 / (1 + np.exp(-g_opp * (self._mu() - mu_opp)))
    
    def _v(self, oppositions):
        sigma = 0
        for opposition in oppositions:
            g_opp = opposition._g()
            E = self._E(opposition)
            sigma += g_opp**2 * E * (1-E)
        return 1 / sigma
    
    def _sum_gsE(self, oppositions, scores):
        sigma = 0
        for opposition, score in zip(oppositions, scores):
            g_opp = opposition._g()
            E = self._E(opposition)
            sigma += g_opp * (score - E)
        return sigma

    def _update_volatility(self, delta, v):
        phi = self._phi()
        A = a = np.log(self._volatility**2)

        def f(x):
            term_1 = np.exp(x) * (delta**2 - phi**2 - v - np.exp(x)) / 2 / (phi**2 + v + np.exp(x))**2
            term_2 = (x-a) / Player.TAU**2
            return term_1 - term_2

        if delta**2 > phi**2 + v:
            B = np.log(delta**2 - phi**2 + v)
        else:
            k = 1
            while f(a - k * Player.TAU) < 0:
                k += 1
            B = a - k * Player.TAU
        f_A, f_B = f(A), f(B)

        epsilon = 1e-6
        while np.abs(B-A) > epsilon:
            C = A + (A-B) * f_A / (f_B - f_A)
            f_C = f(C)
            if f_C * f_B <= 0:
                A, f_A = B, f_B
            else:
                f_A /= 2
            B, f_B = C, f_C
        self._volatility = np.exp(A/2)
    
    def _new_rd(self):
        return np.sqrt(self._phi()**2 + self._volatility**2)


class Fighter(Player):
    SCORING_DICT = {'win': {'KO/TKO': 1, 'SUB': 1, 'U-DEC': 0.95, 'M-DEC': 0.925, 'S-DEC': 0.9, 'DQ': 0.6},
                   'loss': {'KO/TKO': 0, 'SUB': 0, 'U-DEC': 0.05, 'M-DEC': 0.075, 'S-DEC': 0.1, 'DQ': 0.4},
                   'draw': 0.5}
    
    def __init__(self, rating=1500, rd=350, volatility=0.06):
        super().__init__(rating, rd, volatility)
        self.streak = 0
        self.best_streak = 0

    def update(self, oppositions, outcomes, methods):
        scores = self._get_scores(outcomes, methods)
        super().update(oppositions, scores)
        self._update_streak(outcomes)

    def _get_scores(outcomes, methods):
        return [Fighter.SCORING_DICT[outcome][result] if outcome != 'draw'
                else Fighter.SCORING_DICT['draw']
                for outcome, result in zip(outcomes, methods)]
    
    def _update_streak(self, outcomes):
        for outcome in outcomes:
            if outcome == 'win':
                self.streak = 1 if self.streak < 0 else self.streak + 1
                self.best_streak = max(self.streak, self.best_streak)
            elif outcome == 'loss':
                self.streak = -1 if self.streak > 0 else self.streak - 1
            elif outcome == 'draw':
                continue


if __name__ == '__main__':
    players = [Player() for i in range(5)]
    scores = [1, 0, 0.5, 1]
    print([player.rating for player in players])
    print([player._rd for player in players])
    print([player._volatility for player in players])
    players[0].update(players, scores)
    players[1].update([], [])
    print([player.rating for player in players])
    print([player._rd for player in players])
    print([player._volatility for player in players])
import numpy as np


class Fighter:

    TAU = 0.5
    SCORING_DICT = {'win': {'KO/TKO': 1, 'SUB': 1, 'U-DEC': 0.95, 'M-DEC': 0.925, 'S-DEC': 0.9, 'DQ': 0.6},
                   'loss': {'KO/TKO': 0, 'SUB': 0, 'U-DEC': 0.05, 'M-DEC': 0.075, 'S-DEC': 0.1, 'DQ': 0.4},
                   'draw': 0.5}

    def __init__(self, name, rating=1500, rd=350, volatility=0.06):
        self.name = name
        self.rating = rating
        self._rd = rd
        self._volatility = volatility
        self.streak = 0
        self.best_streak = 0

    def update(self, oppositions, outcomes, methods):
        opp_ratings = [opposition.mu for opposition in oppositions]
        opp_rds = [opposition.phi for opposition in oppositions]
        scores = self._get_scores(outcomes, methods)

        self._update_streak(outcomes)

    def _get_scores(outcomes, methods):
        return [Fighter.SCORING_DICT[outcome][result] if outcome != 'draw'
                else Fighter.SCORING_DICT['draw']
                for outcome, result in zip(outcomes, methods)]


    def _update_streak(self, outcomes):
        for outcome in outcomes:
            if outcome == 'win':
                self.streak += 1
                self.best_streak = max(self.streak, self.best_streak)
            elif outcome == 'loss':
                self.streak = -1 if self.streak >= 1 else self.streak - 1

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
        v_opps = 0
        for opposition in oppositions:
            g_opp = opposition._g()
            E = self._E(opposition)
            v_opp = g_opp**2 * E * (1-E)
            v_opps += v_opp
        return 1 / v_opps
    
    def _delta(self, oppositions, scores):
        delta_opps = 0
        for opposition, score in zip(oppositions, scores):
            g_opp = opposition._g()
            E = self._E(opposition)
            delta_opp = g_opp * (score - E)
            delta_opps += delta_opp
        return self._v(oppositions) * delta_opps
    
    def _f(self, oppositions, scores, x):
        a = np.log(self._volatility**2)
        delta = self._delta(oppositions, scores)
        phi = self._phi()
        v = self._v(oppositions)
        term_1 = np.exp(x) * (delta**2 - phi**2 - v - np.exp(x)) / 2 / (phi**2 + v + np.exp(x))**2
        term_2 = (x-a) / Fighter.TAU**2
        return term_1 - term_2

    def _new_volatility(self, oppositions, scores):
        delta = self._delta(oppositions, scores)
        phi = self._phi()
        v = self._v(oppositions)
        A = a = np.log(self._volatility**2)
        k = 1
        if delta**2 > phi**2 + v:
            B = np.log(delta**2 - phi**2 + v)
        else:
            while self._f(a - k * Fighter.TAU) < 0:
                k += 1
            B = a - k * Fighter.TAU
        f_A, f_B = self._f(A), self._f(B)
        while np.abs(B-A) > 1e-6:
            C = A + (A-B) * f_A / (f_B - f_A)
            f_C = self._f(C)
            if f_C * f_B <= 0:
                A, f_A = B, f_B
            else:
                f_A /= 2
            B , f_B = C. f_C
        return np.exp(A/2)
    
    def _new_rd(self):
        return np.sqrt(self._phi()**2 + self._new_volatility()**2)

import numpy as np
from scipy.stats import norm


class Player:
    def __init__(self, rating=1500, rd=350, volatility=0.06, tau=0.5):
        self.rating = rating
        self._rd = rd
        self._volatility = volatility
        self._tau = tau

    def get_rating(self):
        return self.rating
    
    def get_rating_interval(self, confidence=0.95):
        z = norm.ppf(1 - (1-confidence) / 2)
        margin = z * self._rd
        return (float(self.rating - margin), float(self.rating + margin))

    def p_a_beats_b(player_a, player_b):
        rating_a, rating_b = player_a.rating, player_b.rating
        phi_a, phi_b = player_a._phi(), player_b._phi()
        g = 1 / np.sqrt(1 + 3*(phi_a**2 + phi_b**2) / np.pi**2)
        return 1 / (1 + 10**(-g * (rating_a - rating_b) / 400))
    
    def p_win(self, opponent):
        rating, phi = self.rating, self._phi()
        rating_opp, phi_opp = opponent.rating, opponent._phi()
        g = 1 / np.sqrt(1 + 3*(phi**2 + phi_opp**2) / np.pi**2)
        return 1 / (1 + 10**(-g * (rating - rating_opp) / 400))

    def update_rating(self, opponents, scores):
        if len(opponents) == 0:
            self.did_not_compete()
        else:
            v = self._v(opponents)
            sum_gsE = self._sum_gsE(opponents, scores)
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
    
    def _E(self, opponent):
        g_opp = opponent._g()
        mu_opp = opponent._mu()
        return 1 / (1 + np.exp(-g_opp * (self._mu() - mu_opp)))
    
    def _v(self, opponents):
        sigma = 0
        for opponent in opponents:
            g_opp = opponent._g()
            E = self._E(opponent)
            sigma += g_opp**2 * E * (1-E)
        return 1 / sigma
    
    def _sum_gsE(self, opponents, scores):
        sigma = 0
        for opponent, score in zip(opponents, scores):
            g_opp = opponent._g()
            E = self._E(opponent)
            sigma += g_opp * (score - E)
        return sigma

    def _update_volatility(self, delta, v):
        phi = self._phi()
        A = a = np.log(self._volatility**2)

        def f(x):
            term_1 = np.exp(x) * (delta**2 - phi**2 - v - np.exp(x)) / 2 / (phi**2 + v + np.exp(x))**2
            term_2 = (x-a) / self._tau**2
            return term_1 - term_2

        if delta**2 > phi**2 + v:
            B = np.log(delta**2 - phi**2 + v)
        else:
            k = 1
            while f(a - k * self._tau) < 0:
                k += 1
            B = a - k * self._tau
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

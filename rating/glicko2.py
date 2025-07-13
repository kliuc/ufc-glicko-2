import numpy as np
from scipy.stats import norm
import pandas as pd



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
    

    def p_beats(self, opponent):
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



class PlayerManager(dict):

    def __init__(self, ids=[], players=None, volatility=0.06, tau=0.5):
        self._volatility = volatility
        self._tau = tau
        super().__init__({})
        self.add_players(ids, players)


    def add_players(self, ids, players=None):
        if players is None:
            super().update(
                {id: Player(volatility=self._volatility, tau=self._tau)
                 for id in ids if id not in self}
            )
        else:
            if len(ids) != len(players):
                raise Exception('`ids` and `players` must be the same length.')
            super().update(
                {id: player
                 for id, player in zip(ids, players) if id not in self}
            )


    def update_players(self, player_ids, opponent_ids, scores):
        # will update players and opponents corresponding to player_ids and opponent_ids
        competitor_ids = set(player_ids + opponent_ids)
        self.add_players(competitor_ids)
        competitors_copy = {id: self[id] for id in competitor_ids}
        for id, player in self.items():
            if id not in competitor_ids:
                player.did_not_compete()
            else:
                subset = [
                    (opponent_id, score)
                    for player_id, opponent_id, score in zip(player_ids, opponent_ids, scores)
                    if player_id == id
                ]
                opponents_subset, scores_subset = list(zip(*subset))
                player.update_rating(opponents_subset, scores_subset)


    def p_a_beats_b(self, id_a, id_b):
        player_a, player_b = self[id_a], self[id_b]

        rating_a, rating_b = player_a.rating, player_b.rating
        phi_a, phi_b = player_a._phi(), player_b._phi()

        g = 1 / np.sqrt(1 + 3*(phi_a**2 + phi_b**2) / np.pi**2)
        return 1 / (1 + 10**(-g * (rating_a - rating_b) / 400))


    def get_matchups_matrix(self, ids=None):
        if ids is None:
            ids = self.keys()

        ratings = np.array([self[id].rating for id in ids])
        phis2 = np.array([self[id]._phi() for id in ids])**2

        g = 1 / np.sqrt(1 + 3*(phis2[:, None] + phis2) / np.pi**2)
        matchups_matrix = 1 / (1 + 10**(-g * (ratings[:, None] - ratings) / 400))

        return pd.DataFrame(matchups_matrix, index=ids, columns=ids)



if __name__ == '__main__':

    player_a = Player(rating=1800)
    player_b = Player(rating=1500, rd=500)
    player_c = Player(rating=1300)
    player_d = Player(rating=2100)
    manager = PlayerManager(ids=['jon', 'dan', 'matt', 'tom'], players=[player_a, player_b, player_c, player_d])
    print(manager.get_matchups_matrix().loc['tom'])

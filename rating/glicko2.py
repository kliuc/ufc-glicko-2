"""Glicko-2 rating system implementation.

Classes:
    Player -- participant in the Glicko-2 rating system
    PlayerManager -- extends `dict` to handle colletion and batch updates of players
"""

import numpy as np
from scipy.stats import norm
import pandas as pd


class Player:
    """Participant in the Glicko-2 rating system.
    
    Instance Variables:
        rating (float) -- player's rating
        rd (float) -- rating deviation (RD) from Glicko-2 algorithm
        volatility (float) -- volatility (sigma) from Glicko-2 algorithm
    Methods:
        get_rating -- get the rating
        get_rating_interval -- get a confidence interval for the rating
        p_beats -- get the probability of winning versus an opponent
        update_rating -- update the rating, rd, and volatility according to Glicko-2
        did_not_compete -- update the rd in the case of non-compete
    """

    def __init__(self, rating=1500, rd=350, volatility=0.06, tau=0.5):
        """Initialize the player.
        
        Args:
            rating (float) -- initial rating (default 1500)
            rd (float) -- initial rating deviation (RD) (default 350)
            volatility (float) -- initial volatility (default 0.06)
            tau (float) -- parameter (from Glicko-2) that constrains change in volatility (default 0.5)
        """
        self.rating = rating
        self.rd = rd
        self.volatility = volatility
        self._tau = tau

    def get_rating(self):
        """Get the rating."""
        return self.rating
    
    def get_rating_interval(self, confidence=0.95):
        """Get a confidence interval for the rating.

        Args:
            confidence (float) -- confidence level of the confidence interval (default: 0.95)
        Returns:
            tuple[float, float] -- lower bound, upper bound of the confidence interval
        """
        z = norm.ppf(1 - (1-confidence) / 2)
        margin = z * self.rd
        return (float(self.rating - margin), float(self.rating + margin))
    
    def p_beats(self, opponent):
        """Get the probability of winning versus an opponent.
        
        Args:
            opponent (Player) -- the opposing player
        Returns:
            float -- probability of winning
        """
        rating, phi = self.rating, self._phi()
        rating_opp, phi_opp = opponent.rating, opponent._phi()
        g = 1 / np.sqrt(1 + 3*(phi**2 + phi_opp**2) / np.pi**2)
        return 1 / (1 + 10**(-g * (rating - rating_opp) / 400))

    def update_rating(self, opponents, scores):
        """Update the rating, rd, and volatility according to Glicko-2.
        
        Args:
            opponents (List[Player]) -- list of opponents
            scores (List[float]) -- list of scores corresponding to results against opponents
        """
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
            self.rd =  173.7178 * phi

    def did_not_compete(self):
        """Update the rd in the case of non-compete."""
        phi = self._new_rd()
        self.rd = 173.7178 * phi

    def _mu(self):
        return (self.rating - 1500) / 173.7178
    
    def _phi(self):
        return self.rd / 173.7178
    
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
        A = a = np.log(self.volatility**2)

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
        self.volatility = np.exp(A/2)
    
    def _new_rd(self):
        return np.sqrt(self._phi()**2 + self.volatility**2)


class PlayerManager(dict):
    """Extends `dict` to handle colletion and batch updates of players.

    Methods:
        add_players -- add players to manager
        update_players -- batch update players in the manager
        p_a_beats_b -- get probability of matchup between two players
        get_matchups_matrix -- get probability matrix for all matchups of specified players
    """

    def __init__(self, ids=None, players=None, volatility=0.06, tau=0.5):
        """Initialize the manager.

        Args:
            ids (list) -- list of player indices (default None)
            players (list[Player]) -- `Player` objects corresponding to the ids (default None)
            volatility (float) -- initial volatility to be set for new players (default 0.06)
            tau (float) -- tau parameter used to compute player updates (default 0.5)
        """
        if ids is None:
            ids = []
        self._volatility = volatility
        self._tau = tau
        super().__init__()
        self.add_players(ids, players)

    def add_players(self, ids, players=None):
        """Add players to manager.

        Args:
            ids (list) -- player indices to add
            players (list[Player]) -- `Player` objects corresponding to indices (default None)
        """
        if players is None:
            super().update(
                {idx: Player(volatility=self._volatility, tau=self._tau)
                 for idx in ids if idx not in self}
            )
        else:
            if len(ids) != len(players):
                raise Exception('`ids` and `players` must be the same length.')
            super().update(
                {idx: player
                 for idx, player in zip(ids, players) if idx not in self}
            )

    def update_players(self, player_ids, opponent_ids, scores):
        """Batch update players in the manager.

        Args:
            player_ids -- ids of the players that will be updated
            opponent_ids -- ids of the opponents that will also be updated
            scores -- scores of the matchups from players' perspectives
        """
        competitor_ids = set(player_ids + opponent_ids)
        self.add_players(competitor_ids)
        competitors_copy = {idx: self[idx] for idx in competitor_ids}
        update_dict = {
            idx: {'opponents': [], 'scores': []}
            for idx in competitor_ids
        }
        for player_id, opponent_id, score in zip(player_ids, opponent_ids, scores):
            update_dict[player_id]['opponents'].append(competitors_copy[opponent_id])
            update_dict[opponent_id]['opponents'].append(competitors_copy[player_id])
            update_dict[player_id]['scores'].append(score)
            update_dict[opponent_id]['scores'].append(1-score)
        for idx, player in self.items():
            if idx not in competitor_ids:
                player.did_not_compete()
            else:
                new_opponents = update_dict[idx]['opponents']
                new_scores = update_dict[idx]['scores']
                player.update_rating(new_opponents, new_scores)

    def p_a_beats_b(self, id_a, id_b):
        """Get probability of matchup between two players.

        Args:
            id_a (Player) -- id of player from which probability is computed
            id_b (Player) -- id of player from which probability is computed against
        Returns:
            float -- probability that player a (id_a) will beat player b (id_b)
        """
        player_a, player_b = self[id_a], self[id_b]
        rating_a, rating_b = player_a.rating, player_b.rating
        phi_a, phi_b = player_a._phi(), player_b._phi()
        g = 1 / np.sqrt(1 + 3*(phi_a**2 + phi_b**2) / np.pi**2)
        return 1 / (1 + 10**(-g * (rating_a - rating_b) / 400))

    def get_matchups_matrix(self, ids=None):
        """Get probability matrix for all matchups of specified players.

        Args:
            ids (list) -- list of player indices (default None)
        Returns:
            pd.DataFrame -- square matrix where (i, j) is probability of player i beating player j
            if ids is None then all players are included in the matrix
        """
        if ids is None:
            ids = self.keys()
        ratings = np.array([self[idx].rating for idx in ids])
        phis2 = np.array([self[idx]._phi() for idx in ids])**2
        g = 1 / np.sqrt(1 + 3*(phis2[:, None] + phis2) / np.pi**2)
        matchups_matrix = 1 / (1 + 10**(-g * (ratings[:, None] - ratings) / 400))
        return pd.DataFrame(matchups_matrix, index=ids, columns=ids)


if __name__ == '__main__':
    player_a = Player(rating=1800)
    player_b = Player(rating=1500, rd=500)
    player_c = Player(rating=1300)
    player_d = Player(rating=2100)
    manager = PlayerManager(
        ids=['jon', 'dan', 'matt', 'tom'],
        players=[player_a, player_b, player_c, player_d]
    )
    print(manager.get_matchups_matrix())
    manager.update_players(
        player_ids=['tom', 'tom'],
        opponent_ids=['jon', 'dan'],
        scores=[1, 1]
    )
    print(manager.get_matchups_matrix())
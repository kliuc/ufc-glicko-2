# UFC Glicko-2-based Rating System

<img width="715" height="439" alt="image" src="https://github.com/user-attachments/assets/24e00bc7-1579-4f36-8058-7a2f09800df0" />

*Screenshot from the [web app](https://ufc-glicko-2.streamlit.app/Rating_Plots)*

## Introduction

Who is the UFC G.O.A.T.? Some argue it's Jon Jones, others say it's GSP, or even Mighty Mouse. In this project I attempt to answer this question more objectively by applying the Glicko-2 rating algorithm. Using fight results from the UFC’s modern era, I apply Glicko-2 to rate fighters based solely on their UFC performances.

Glicko-2 is a rating algorithm developed by [Dr. Mark Glickman](https://www.glicko.net/index.html) as an improvement to the [Elo rating system](https://en.wikipedia.org/wiki/Elo_rating_system). Both systems work by assessing two-player games and adjusting each player's rating based on the result. The most well-known application of Glicko is in online chess platforms ([see Chess.com](https://support.chess.com/en/articles/8566476-how-do-ratings-work-on-chess-com)), but it is also a powerful tool for evaluating competitors in any one-on-one sport. Here we implement the algorithm to rate UFC fighters to identify the most skillful competitors.

The benefit of using Glicko-2 over traditional rating systems (like Elo) is that Glicko-2 accounts for uncertainty in ratings. Specifically, Glicko-2 takes a Bayesian approach by modeling player skill as a probability distribution (instead of a single value). This is a critical feature that makes Glicko-2 a great choice for computing ratings in the UFC, where upsets and evolving skill sets make it difficult to assign static ratings.

## Usage

I have made my implementations of Glicko-2 and UFC-specific Glicko-2 available in the repo as Python modules. The UFC fighter ratings dataset is also available and is automatically updated weekly (after UFC events) via GitHub Actions. There is also a web app to explore the ratings! If interested, the Glicko-2 algorithm optimization procedures are also available as Jupyter notebook.

### [Web App](https://ufc-glicko-2.streamlit.app/)
Explore the data!

### [Glicko-2 Implementation](https://github.com/kliuc/ufc-glicko-2/tree/main/rating)
Make your own Glicko-2 rating system!

### [Ratings Dataset](https://github.com/kliuc/ufc-glicko-2/blob/main/data/ratings.csv)
Download the data and create models!

### [Optimization](https://github.com/kliuc/ufc-glicko-2/blob/main/optimization.ipynb)
See the optimization procedures!

## References

Glickman, Mark E., et al. “A Comparison of Rating Systems for Competitive Womens’s Beach Volleyball.” *Statistica Applicata*, vol. 30, no. 2, Aug. 2018, pp. 233–54. *DOI.org (CSL JSON)*, https://doi.org/10.26398/IJAS.0030-010.

Glickman, Mark E. *Example of the Glicko-2 System*. Mar. 2022, https://www.glicko.net/glicko/glicko2.pdf.





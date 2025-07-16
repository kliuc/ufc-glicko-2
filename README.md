# UFC Glicko-2-based Rating System

<img width="715" height="439" alt="image" src="https://github.com/user-attachments/assets/24e00bc7-1579-4f36-8058-7a2f09800df0" />

*Screenshot from the [web app](https://ufc-glicko-2.streamlit.app/Rating_Plots)*

## Introduction

Who is the UFC G.O.A.T.? Some argue it's Jon Jones, others say it's GSP, or even Mighty Mouse. In this project I attempt to answer this question more objectively by applying the Glicko-2 rating algorithm. Using fight results from the UFC’s modern era, I apply Glicko-2 to rate fighters based solely on their UFC performances.

Glicko-2 is a rating algorithm developed by [Dr. Mark Glickman](https://www.glicko.net/index.html) as an improvement to the [Elo rating system](https://en.wikipedia.org/wiki/Elo_rating_system). Both systems work by assessing two-player games, and adjusting each player's rating based on the result. The most well-known application of Glicko is in online chess player ratings ([see Chess.com](https://support.chess.com/en/articles/8566476-how-do-ratings-work-on-chess-com)). Here we implement the algorithm to rate UFC fighters to identify the most skillful competitors.

The benefit of using Glicko-2 over traditional rating systems (like Elo) is that Glicko-2 accounts for uncertainty in ratings. This is a critical feature that makes Glicko-2 effective for computing ratings in the UFC, where upsets and evolving skill sets make it difficult to assign static ratings.

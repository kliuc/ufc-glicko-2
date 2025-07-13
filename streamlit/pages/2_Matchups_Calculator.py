import streamlit as st
import pandas as pd


@st.cache_data
def load_matchups_matrix():
    return pd.read_csv('data/matchups-matrix.csv', index_col=0)

st.set_page_config(page_title='Matchups Calculator')

st.write('## Matchups Calculator')
st.write('Choose any two fighters and predict the winner!')

matchups_matrix = load_matchups_matrix()

l_column, m_column, r_column = st.columns(3)

fighter_a = l_column.selectbox('Select fighter A', matchups_matrix.index)
m_column.html('<h2 style="text-align:center;">vs.</h2>')
fighter_b = r_column.selectbox('Select fighter B', matchups_matrix.index)

if st.button('Calculate'):
    if fighter_a == fighter_b:
        st.write('#### Please select two unique fighters.')
    else:
        p = matchups_matrix.loc[fighter_a, fighter_b]
        winner = fighter_a if p >= 0.5 else fighter_b
        p = max(p, 1-p)
        st.write(f'#### {winner} wins with estimated {p:.2%} chance.')
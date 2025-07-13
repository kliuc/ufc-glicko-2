import streamlit as st
import pandas as pd
import numpy as np


@st.cache_data
def load_matchups_matrix():
    return pd.read_csv('data/matchups-matrix.csv', index_col=0)

@st.cache_data
def get_predictions():
    matchups_matrix = load_matchups_matrix()
    upcoming_fights = pd.read_json('data/upcoming_fights.json')
    
    ps = matchups_matrix.loc[upcoming_fights['fighter_a'], upcoming_fights['fighter_b']]
    upcoming_fights['p'] = np.diag(ps)

    upcoming_fights['winner'] = upcoming_fights.apply(
        lambda x: x['fighter_a'] if x['p']>=0.5 else x['fighter_b'],
        axis=1
    )
    
    upcoming_fights['p'] = np.maximum(upcoming_fights['p'], 1-upcoming_fights['p'])
    upcoming_fights['p'] = upcoming_fights['p'].apply(lambda x: f'({x:.0%})')
    
    upcoming_fights['winner'] += ' ' + upcoming_fights['p']
    upcoming_fights = upcoming_fights.rename(
         columns={
             'weight_class': 'Weight Class',
             'fighter_a': 'Fighter A',
             'fighter_b': 'Fighter B',
             'winner': 'Winner'
         }
    )
    
    return upcoming_fights.groupby('event', sort=False)

st.set_page_config(page_title='Upcoming Events')

st.write('## Upcoming Events')
st.write('Choose any upcoming event and see the fight predictions!')

predictions = get_predictions()

event = st.selectbox('Select an upcoming event', predictions.groups.keys())

st.table(predictions.get_group(event)[['Weight Class', 'Fighter A', 'Fighter B', 'Winner']])
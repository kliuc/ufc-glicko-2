import streamlit as st
import pandas as pd
import json
import altair as alt


@st.cache_data
def load_histories():
    with open('data/rating-histories.json', 'r') as f:
        return json.load(f)
    
st.set_page_config(page_title='Rating Plots')

st.write('## Rating Plots')
st.write('Search for your favorite fighter(s) and explore their rating history!')

histories = load_histories()

selected_fighters = st.multiselect('Select fighter(s)', histories.keys(), default=['Charles Oliveira', 'Ilia Topuria', 'Islam Makhachev'])
show_interval = st.toggle('Show confidence interval(s)', value=True)

if selected_fighters:
    histories_flat = [
        {'name': name,
         'timestamp': record['timestamp'],
         'rating': record['rating'],
         'lower': record['lower'],
         'upper': record['upper']}
        for name in selected_fighters
        for record in histories[name]
    ]

    df = pd.DataFrame(histories_flat)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    rating = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('timestamp', title='Date'),
        y=alt.Y('rating', title='Rating'),
        color=alt.Color('name', title='Fighters'),
        tooltip=[]
    )

    if show_interval:
        interval = alt.Chart(df).mark_area(opacity=0.1).encode(
            x='timestamp',
            y='lower',
            y2='upper',
            color=alt.Color('name', legend=None),
            tooltip=[]
        )
        chart = alt.layer(rating, interval).resolve_scale(color='independent')
    
    else:
        chart = rating

    st.altair_chart(chart.interactive())
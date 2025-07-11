import streamlit as st
import pandas as pd
import json
import altair as alt


@st.cache_data
def load_data():
    pass

st.write('# UFC Glicko-2 Based Rating System')
st.write('### Ratings Table')
st.write('Explore the ratings using the interactive table below! Options for filtering by weight class, sorting, and searching for fighters.')

with st.expander('Select Weightclass(es)'):
    l_column, m_column, r_column = st.columns(3)
    mens_classes = ["Flyweight", "Bantamweight", "Featherweight", "Lightweight", "Welterweight", "Middleweight", "Light Heavyweight", "Heavyweight"]
    womens_classes = ["Women's Strawweight", "Women's Flyweight", "Women's Bantamweight", "Women's Featherweight"]
    check_men = l_column.checkbox('Men', value=True)
    check_women = l_column.checkbox('Women', value=True)
    selected_classes = []
    for wc in mens_classes:
        if m_column.checkbox(wc, value=check_men):
            selected_classes.append(wc)
    for wc in womens_classes:
        if r_column.checkbox(wc, value=check_women):
            selected_classes.append(wc)
ratings_df = pd.read_csv('data/ratings.csv', index_col='name')
filtered_ratings = ratings_df.loc[ratings_df['weight_class'].isin(selected_classes)]

st.write(filtered_ratings.sort_values('peak_rating', ascending=False))
st.link_button('Download the full ratings dataset', 'https://github.com/kliuc/ufc-glicko-2/blob/main/data/ratings.csv')


st.write('### Historical Rating Plots')
st.write('Search for your favorite fighter(s) and explore their rating history!')

with open('data/rating-histories.json', 'r') as f:
    histories = json.load(f)

selected_fighters = st.multiselect('Select fighter(s)', histories.keys(), default=['Charles Oliveira', 'Ilia Topuria', 'Islam Makhachev'])
show_interval = st.toggle('Show Confidence Interval(s)', value=True)

if selected_fighters:
    histories_flat = [{'name': name,
                       'timestamp': record['timestamp'],
                       'rating': record['rating'],
                       'lower': record['lower'],
                       'upper': record['upper']}
                       for name in selected_fighters
                       for record in histories[name]]
    df = pd.DataFrame(histories_flat)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    rating = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('timestamp', title='Date'),
        y=alt.Y('rating', title='Rating'),
        color=alt.Color('name', title='Fighters'),
        tooltip=[])

    if show_interval:
        interval = alt.Chart(df).mark_area(opacity=0.1).encode(
            x='timestamp',
            y='lower',
            y2='upper',
            color=alt.Color('name', legend=None),
            tooltip=[])
        chart = alt.layer(rating, interval).resolve_scale(color='independent')
    else:
        chart = rating

    st.altair_chart(chart.interactive())
        
st.write('### Upcoming Event Predictions')
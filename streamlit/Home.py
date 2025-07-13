import streamlit as st
import pandas as pd


@st.cache_data
def load_ratings():
    return pd.read_csv('data/ratings.csv')

st.set_page_config(page_title='Home')

st.write('# UFC Glicko-2 Based Rating System')
st.write('Check out additional tables and plots using the sidebar!')

st.write('## Ratings Table')
st.write('Explore the ratings using the interactive table below! Options for filtering by weight class, sorting, and searching for fighters.')

with st.expander('Select weightclass(es)'):
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

ratings_df = load_ratings()
filtered_ratings = ratings_df.loc[ratings_df['weight_class'].isin(selected_classes)]
filtered_ratings.columns = ['Name', 'Weight Class', 'Current Rating', 'Peak Rating', 'Current Streak', 'Best Streak']
filtered_ratings.set_index('Name', inplace=True)

st.write(filtered_ratings.sort_values('Peak Rating', ascending=False))
st.link_button('Download the full ratings dataset', 'https://github.com/kliuc/ufc-glicko-2/blob/main/data/ratings.csv')
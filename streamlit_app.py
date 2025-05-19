import streamlit as st
import pandas as pd
from pyvis.network import Network
import tempfile

# --- Your published Google Sheet CSV URL here ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR5LCaBoStnQsD5lUxW3899FvaxN4Gr1D4Yh5mgTHe2k4D6Y31_RVG5wBhtvOWGbgBcajAXzwbOKcf7/pub?gid=844485577&single=true&output=csv"


st.title("💋 Sexytime Network")

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)
    # Fix column names if needed
    df.columns = [col.strip() for col in df.columns]
    return df

def normalize_pairs(df):
    # Sort pairs so (A,B) == (B,A)
    df['pair'] = df.apply(lambda r: tuple(sorted([r['Persoon 1'], r['Persoon 2']])), axis=1)
    return df

def aggregate_pairs(df):
    agg = df.groupby('pair').agg({
        'Muilke gedaan?': lambda x: 'Ja' in x.values,
        'Sexy time?': lambda x: 'Ja' in x.values
    }).reset_index()
    return agg

def draw_network(agg_df):
    net = Network(height="700px", width="100%", notebook=False)
    # Add nodes
    unique_people = set()
    for pair in agg_df['pair']:
        unique_people.update(pair)
    for person in unique_people:
        net.add_node(person, label=person)
    # Add edges with colors
    for _, row in agg_df.iterrows():
        p1, p2 = row['pair']
        kissed = row['Muilke gedaan?']
        fucked = row['Sexy time?']
        if kissed and fucked:
            color = 'purple'
            title = "Kissed & Fucked"
        elif kissed:
            color = 'yellow'
            title = "Kissed"
        elif fucked:
            color = 'blue'
            title = "Fucked"
        else:
            color = 'gray'
            title = "None"
        net.add_edge(p1, p2, color=color, title=title, width=3)
    return net

df = load_data()
df = normalize_pairs(df)
agg = aggregate_pairs(df)

st.subheader("Raw Data")
st.dataframe(df)

st.subheader("Aggregated Pair Interactions")
st.dataframe(agg)

st.subheader("Interactive Network Graph")

net = draw_network(agg)
with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
    net.save_graph(tmp.name)
    html = open(tmp.name, 'r', encoding='utf-8').read()
    st.components.v1.html(html, height=750, scrolling=True)

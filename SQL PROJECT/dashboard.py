import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import sqlite3
import base64

# Function to set a local background image
def set_bg_local(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Call the function with your image filename
set_bg_local("background.jpg")

# ---------- Connect to Database ----------
conn = sqlite3.connect("factbook.db")
df = pd.read_sql_query("SELECT * FROM facts", conn)

st.title(" Global Demographics Dashboard")
st.markdown("Explore population, growth, and area statistics using CIA World Factbook data.")

# ---------- Sidebar Filters ----------
st.sidebar.header("Filters")

min_pop = st.sidebar.number_input("Minimum Population", min_value=int(df['population'].min()), 
                                  max_value=int(df['population'].max()), value=1000000, step=1000000)
max_pop = st.sidebar.number_input("Maximum Population", min_value=int(df['population'].min()), 
                                  max_value=int(df['population'].max()), value=int(df['population'].max()), step=1000000)

min_area = st.sidebar.number_input("Minimum Area", min_value=int(df['area'].min()), 
                                   max_value=int(df['area'].max()), value=0, step=1000)
max_area = st.sidebar.number_input("Maximum Area", min_value=int(df['area'].min()), 
                                   max_value=int(df['area'].max()), value=int(df['area'].max()), step=1000)

min_growth = st.sidebar.slider("Minimum Population Growth (%)", float(df['population_growth'].min()), 
                               float(df['population_growth'].max()), 0.0, step=0.01)
max_growth = st.sidebar.slider("Maximum Population Growth (%)", float(df['population_growth'].min()), 
                               float(df['population_growth'].max()), float(df['population_growth'].max()), step=0.01)

# Apply filters
filtered_df = df[(df['population'] >= min_pop) & (df['population'] <= max_pop) &
                 (df['area'] >= min_area) & (df['area'] <= max_area) &
                 (df['population_growth'] >= min_growth) & (df['population_growth'] <= max_growth)]

# ---------- Download Button ----------
st.sidebar.markdown("### Download Filtered Data")
csv = filtered_df.to_csv(index=False)
st.sidebar.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_factbook_data.csv",
    mime="text/csv"
)

# ---------- Organized Layout with Tabs ----------
tabs = st.tabs(["Bar Charts", "Scatter Plot", "Choropleth Maps"])

# ------------- Tab 1: Bar Charts -------------
with tabs[0]:
    st.subheader("Top 10 Countries by Population")
    top_pop = filtered_df.sort_values(by='population', ascending=False).head(10)
    fig1, ax1 = plt.subplots()
    sns.barplot(x='population', y='name', data=top_pop, palette='viridis', ax=ax1)
    st.pyplot(fig1)

    st.subheader("Top 10 Countries by Area")
    top_area = filtered_df.sort_values(by='area', ascending=False).head(10)
    fig2, ax2 = plt.subplots()
    sns.barplot(x='area', y='name', data=top_area, palette='plasma', ax=ax2)
    st.pyplot(fig2)

    st.subheader("Top 10 Fastest Growing Populations")
    top_growth = filtered_df.sort_values(by='population_growth', ascending=False).head(10)
    fig3, ax3 = plt.subplots()
    sns.barplot(x='population_growth', y='name', data=top_growth, palette='cividis', ax=ax3)
    st.pyplot(fig3)

# ------------- Tab 2: Scatter Plot -------------
with tabs[1]:
    st.subheader("Population vs Area")
    fig4 = px.scatter(filtered_df, x='area', y='population', hover_name='name',
                      log_x=True, log_y=True, color='population_growth',
                      color_continuous_scale='Viridis', size='population')
    st.plotly_chart(fig4)

# ------------- Tab 3: Choropleth Maps -------------
with tabs[2]:
    st.subheader("Population by Country")
    fig5 = px.choropleth(filtered_df, locations='code', locationmode='ISO-3',
                         color='population', hover_name='name',
                         color_continuous_scale='Viridis')
    st.plotly_chart(fig5)

    st.subheader("Population Growth by Country")
    fig6 = px.choropleth(filtered_df, locations='code', locationmode='ISO-3',
                         color='population_growth', hover_name='name',
                         color_continuous_scale='Plasma')
    st.plotly_chart(fig6)

    st.subheader("Country Area")
    fig7 = px.choropleth(filtered_df, locations='code', locationmode='ISO-3',
                         color='area', hover_name='name',
                         color_continuous_scale='Cividis')
    st.plotly_chart(fig7)

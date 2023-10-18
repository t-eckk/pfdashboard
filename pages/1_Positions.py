import streamlit as st
import pdboard
import pandas as pd
import plotly.express as px

st.title('Positions')

positions = pdboard.get_positions()

st.dataframe(positions)

fig = px.pie(names=positions.index, values=positions['total'])

st.plotly_chart(fig)
import streamlit as st
import pdboard
import pandas as pd
import plotly.express as px

st.title('Alpha Positioning')

positions = pdboard.get_positions()
nav = positions['total'].sum()

alpha_port = pdboard.get_alpha_portfolio()

st.dataframe(alpha_port.groupby('ticker').sum())

st.table(pdboard.get_alpha_volatility())
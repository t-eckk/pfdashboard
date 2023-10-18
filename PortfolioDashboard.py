import streamlit as st
import pdboard

universe = pdboard.get_universe()
st.dataframe(universe)

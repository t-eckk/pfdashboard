import streamlit as st
import pandas as pd
import yfinance as yf
import pdboard
import plotly.express as px

st.title('Transactions & Cash Flows')
universe = pdboard.get_universe()

with st.form('Stock Info', False):
    st.subheader('Quick info')
    
    ticker = st.selectbox('Ticker', universe)
    
    btn = st.form_submit_button('Retrieve')
    
    if btn:
        stock = yf.download(ticker)['Close'].iloc[-252:]
        fig = px.line(stock)
        st.plotly_chart(
            fig
        )
    
with st.form('new_order', False):
    st.subheader('New Transaction')
    col1, col2 = st.columns(2)
    side = col2.selectbox('Side', ['BUY', 'SELL'])
    ticker = col1.selectbox('Ticker', universe)
    date = st.date_input('Date')
    
    col1, col2 = st.columns(2)
    exec_price = col1.number_input('Execution Price')
    quantity = col2.number_input('Quantity')
    commissions = col1.number_input('Commissions (total)')
    comment = col2.text_input('Comment')
    
    btn = st.form_submit_button('Submit')
    
    if btn:
        order = pdboard.create_order(ticker, side, date, exec_price, quantity, commissions, comment)
        pdboard.save_order(order)
       
with st.form('cash_flow', False):
    st.subheader('New Cash Flow')
    col1, col2 = st.columns(2)
    side = st.selectbox('Type', ['Inflow', 'Outflow', 'Corporate Action'])
    #ticker = col2.selectbox('Ticker (if corporate action)', universe)
    ticker = 'CASH'
    date = st.date_input('Date')
    
    col1, col2 = st.columns(2)
    amount = col1.number_input('Amount')
    comment = col2.text_input('Comment')
    
    btn = st.form_submit_button('Submit')
    
    if btn:
        cashflow = pdboard.create_cashflow(ticker, side, date, amount, comment)
        pdboard.save_cashflow(cashflow)
#%%
import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import datetime as dt
from pandas.tseries.offsets import BusinessDay

@st.cache_data
def get_universe():
    return pd.read_json('universe.json')[0].rename('Universe')

def create_order(ticker, side, date, price, quantity, commissions, comment, strategy):
    quantity = quantity if side == 'BUY' else quantity * -1
    out = pd.DataFrame({
        'side': side, 
        'date': date,
        'price': price, 
        'quantity': quantity,
        'commissions': commissions,
        'comment': comment,
        'strategy': strategy},
        index=[ticker]
    )
    out.index.name = 'ticker'
    return out

def create_cashflow(ticker, side, date, amount, comment):
    amount = amount if side != 'Outflow' else amount * -1
    ticker = 'CASH'
        
    out = pd.DataFrame({
        'side': side,
        'date': date,
        'amount': amount,
        'comment': comment},
        index=[ticker]
    )
    out.index.name = 'ticker'
    return out

def save_order(order):
    orders = pd.read_csv('operations/orders.csv', index_col=0)
    orders = pd.concat([orders, order])
    orders.to_csv('operations/orders.csv')

def save_cashflow(cashflow):
    cashflows = pd.read_csv('operations/cashflows.csv', index_col=0)
    cashflows = pd.concat([cashflows, cashflow])
    cashflows.to_csv('operations/cashflows.csv')

def get_positions(date = '2100-01-01', roundbool=True):
    orders = pd.read_csv('operations/orders.csv', index_col=0)
    orders = orders.reset_index().set_index('date')
    orders.index = pd.to_datetime(orders.index)
    orders = orders[:date]
    orders['total'] = orders['quantity'] * orders['price']

    cashflows = pd.read_csv('operations/cashflows.csv', index_col=0)
    cashflows = cashflows.reset_index().set_index('date')
    cashflows.index = pd.to_datetime(cashflows.index)
    cashflows = cashflows[:date]

    current_cash = cashflows['amount'].sum() - orders['total'].sum() - orders['commissions'].sum()

    positions = orders.groupby('ticker').sum()['quantity'].to_frame()
    positions.loc['CASH'] = current_cash
    
    tickers = list(orders['ticker'].unique())
    if date == '2100-01-01':
        date = dt.datetime.today() - BusinessDay(1) 
        date = str(date)[:10]
    try:
        last = yf.download(tickers, start=date)['Close'].loc[date]
        print(last)
    except:
        return 
    
    last = last.T
    
    try:
        last.columns = ['price']
        last.loc['CASH'] = 1
    except:
        last = pd.Series([last, 1], index=['price', 'CASH'])
    
    positions['price'] = last
    toobig = positions['price'] > 250
    positions['price'].loc[toobig] /= 100
    
    positions['total'] = positions['quantity'] * positions['price']
    positions['%weight'] = 100 * positions['total'] / positions['total'].sum()
    
    return positions.round(2) if roundbool else positions

def get_alpha_portfolio(date = '2100-01-01', roundbool=True):
    nav = get_positions(roundbool=False)['total'].sum()
    orders = pd.read_csv('operations/orders.csv', index_col=0)
    orders = orders.reset_index().set_index('date')
    orders.index = pd.to_datetime(orders.index)
    orders = orders[:date]
    orders['total'] = orders['quantity'] * orders['price']
    orders = orders[orders['strategy'].str.contains('ALPHA')]
    
    positions = orders.groupby(['ticker', 'strategy']).sum()['quantity'].to_frame()
    positions = positions.reset_index().set_index('ticker')
    
    tickers = list(orders['ticker'].unique())
    last = yf.download(tickers, period='1d')['Close']
    last = last.T
    last.columns = ['price']
    last.loc['CASH'] = 1
    
    positions['price'] = last
    toobig = positions['price'] > 250
    positions['price'].loc[toobig] /= 100
    
    positions['total'] = positions['quantity'] * positions['price']
    positions['%weight'] = 100 * positions['total'] / nav
    
    positions = positions.sort_values(by='strategy')
    return positions.round(2) if roundbool else positions
    
def get_alpha_volatility(date = '2100-01-01', roundbool=True):
    alpha_positions = get_alpha_portfolio(roundbool=False)
    aggregated_positions = alpha_positions.groupby('ticker').sum()
    tickers = list(aggregated_positions.index)

    df = yf.download(tickers, period='3y')['Adj Close'].fillna(method='ffill').dropna()
    returns = np.log(1+df.pct_change())
    
    backtest = (returns * aggregated_positions['%weight'] / 100).sum(axis=1)
    backtest = backtest.iloc[-252:]
    
    year = backtest.std() * 16 * 100
    quarter = backtest.iloc[-63:].std() * 16 * 100
    alpha_book = pd.Series([year, quarter], index=['1y lookback', '3m lookback'], name='Alpha Volatility (%)').to_frame().T
    pf = [year, quarter]
    strategies = alpha_positions['strategy'].unique()
    
    for strategy in strategies:
        backtest = (returns * alpha_positions[alpha_positions['strategy'] == strategy]['%weight'] / 100).sum(axis=1)
        year = backtest.std() * 16 * 100
        quarter = backtest.iloc[-63:].std() * 16 * 100
        alpha_book.loc[strategy] = [year, quarter]

    alpha_book = alpha_book.sort_values(by='1y lookback')
    alpha_book.drop('Alpha Volatility (%)', inplace=True)
    alpha_book.loc['Alpha Volatility (%)'] = pf
    return alpha_book[::-1]
    
def get_average_entry():
    pass

def portfolio_balance():
    orders = pd.read_csv('operations/orders.csv', index_col=0)
    orders['total'] = orders['quantity'] * orders['price']
    
    cashflows = pd.read_csv('operations/cashflows.csv', index_col=0)
    universe = get_universe()
    
    
    orders.groupby('ticker').sum()

def init():
    orders = pd.DataFrame(
        columns=['ticker', 'side', 'date', 'price', 'quantity', 'commissions', 'comment']
    ).set_index('ticker', drop=True)
    cashflows = pd.DataFrame(
        columns=['ticker', 'side', 'date', 'amount', 'comment']
    ).set_index('ticker', drop=True)
    orders.to_csv('operations/orders.csv')
    cashflows.to_csv('operations/cashflows.csv')
    
if __name__ == '__main__':
    pass
    #init()
# %%

# %%

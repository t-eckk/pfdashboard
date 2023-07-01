#%%
import pandas as pd
import streamlit as st

@st.cache_data
def get_universe():
    return pd.read_json('universe.json')[0].rename('Universe')

def create_order(ticker, side, date, price, quantity, commissions, comment):
    quantity = quantity if side == 'BUY' else quantity * -1
    out = pd.DataFrame({
        'side': side, 
        'date': date,
        'price': price, 
        'quantity': quantity,
        'commissions': commissions,
        'comment': comment},
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

def portfolio_balance():
    orders = pd.read_csv('operations/orders.csv', index_col=0)
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
orders = pd.read_csv('operations/orders.csv', index_col=0)
universe = get_universe()


# %%

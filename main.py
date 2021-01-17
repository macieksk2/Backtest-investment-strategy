# -*- coding: utf-8 -*-
"""
@author: maciej_sliz
"""
# Import packages
import os
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
########################################################################
# INPUT
########################################################################

# Read in input historical data:
# Historical level of Dow Jones Composite Index
# Historical TLT 20Y ETF Index level
historicals = pd.read_csv("DJ_TLT_backtesting.csv", sep = ";")

########################################################################
# PARAMETERS:
########################################################################

# The strategy parameters:
# Starting Value
starting_value = 100000
# Share of equities initially
starting_equity_share = 0.8
# Share of bonds intitally
starting_bond_share = 0.2

# Charge Equity
eq_chrg = 0.003
# Charge Bond
bond_chrg = 0.002
# Min time between rebalances (in trading days)
min_time_rebalance = 30
# Share of bonds sold when increasing stocks position
share_bond_sold_when_incr_stock = 1.0
# Share of stocks sold when increasing bonds position
share_stock_sold_when_incr_bond = 0.0
# Share of stocks sold when decreasing stocks position
share_stock_bought_when_decr_bond = 1.0
# Share of bonds sold when decreasing bonds position
share_bond_bought_when_decr_stock = 1.0
# Shorter term MA window (in trading days)
short_MA = 30
# Longer term MA window (in trading days)
long_MA = 200
# Upper bound of DJ/TLT ratio
upper_DJ_TLT = 0.7
# Lower bound of DJ/TLT ratio
lower_DJ_TLT = 0.4

########################################################################
# CALCULATION:
########################################################################
# Calculate first day of backtesting based on the length of longer term MA
first_day_backtest = historicals.iloc[long_MA - 1]["Date"]
# first_day_backtest = datetime.strptime(first_day_backtest , '%Y-%m-%d')

# Define the array with historical portfolio, split by stocks and bonds
portfolio = pd.DataFrame(0.0, index=historicals['Date'], columns=['Stocks','Bonds','Portfolio'])
# Define the array with MA and DJ/TLT ratio
MA = pd.DataFrame(0.0, index=historicals['Date'], columns=['DJ short','DJ long','Bond short', 'Bond long', 'DJ/TLT'])
# Define the array with transactions
transactions = pd.DataFrame(0.0, index=historicals['Date'], columns=['Stocks','Bonds'])
# Define the array with value of transactions
transactions_values = pd.DataFrame(0.0, index=historicals['Date'], columns=['Stocks','Bonds'])

# Iterate through all historical dates
for n in range(len(historicals)):
    # Check if date is after the starting date
    if historicals.iloc[n]["Date"] >= first_day_backtest:
        # Calculate short term MA - DJ
        MA.iloc[n]["DJ short"] = np.mean(historicals.iloc[range(n-short_MA+1,n+1)]["DOW JONES COMPOSITE"].astype(float)) 
        # Calculate long term MA - DJ
        MA.iloc[n]["DJ long"] = np.mean(historicals.iloc[range(n-long_MA+1,n+1)]["DOW JONES COMPOSITE"].astype(float))      
        # Calculate short term MA - TLT
        MA.iloc[n]["Bond short"] = np.mean(historicals.iloc[range(n-short_MA+1,n+1)]["TLT 20Y"].astype(float))        
        # Calculate long term MA - TLT
        MA.iloc[n]["Bond long"] = np.mean(historicals.iloc[range(n-long_MA+1,n+1)]["TLT 20Y"].astype(float))            
        # Calculate DJ/TLT ratio, check whether stock price and TLT index are within the bounds
        MA.iloc[n]["DJ/TLT"] = round(np.float(historicals.iloc[n]["DOW JONES COMPOSITE"] / historicals.iloc[n]["TLT 20Y"]),5)           
    if historicals.iloc[n]["Date"] > first_day_backtest:  
        # Has short term MA crossed long term MA?
        # Has it crossed it from below? -> BUY MORE DJ
        # Has DJ/TLT crossed lower bound from above? -> BUY MORE DJ
        if (MA.iloc[n]["DJ short"] > MA.iloc[n]["DJ long"] and MA.iloc[n-1]["DJ short"] < MA.iloc[n-1]["DJ long"]) or (MA.iloc[n]["DJ/TLT"] <= lower_DJ_TLT * 100 and MA.iloc[n-1]["DJ/TLT"] > lower_DJ_TLT * 100):
            transactions.iloc[n]['Stocks'] = 1
        # Has it crossed it from above? -> SELL MORE DJ 
        # Has DJ/TLT crossed upper bound from below? -> SELL MORE DJ 
        elif (MA.iloc[n]["DJ short"] < MA.iloc[n]["DJ long"] and MA.iloc[n-1]["DJ short"] > MA.iloc[n-1]["DJ long"]) or (MA.iloc[n]["DJ/TLT"] >= upper_DJ_TLT * 100 and MA.iloc[n-1]["DJ/TLT"] < upper_DJ_TLT * 100):
            transactions.iloc[n]['Stocks'] = -1
        else:
            transactions.iloc[n]['Stocks'] = 0
        
        # TLT
        if MA.iloc[n]["Bond short"] > MA.iloc[n]["Bond long"] and MA.iloc[n-1]["Bond short"] < MA.iloc[n-1]["Bond long"]:
            transactions.iloc[n]['Bonds'] = 1
        # Has it crossed it from above? -> SELL MORE TLT 
        elif MA.iloc[n]["Bond short"] < MA.iloc[n]["Bond long"] and MA.iloc[n-1]["Bond short"] > MA.iloc[n-1]["Bond long"]:
            transactions.iloc[n]['Bonds'] = -1   
        else:
            transactions.iloc[n]['Bonds'] = 0
        
        # If the transaction is to be done, check if enough time passed from the last trade by verifing if both minimum and maximum of the transactions are equal to 0
        if transactions.iloc[n]['Stocks'] == 1 and np.min(transactions.iloc[range(n-min_time_rebalance,n)]["Stocks"].astype(float)) == 0 and np.max(transactions.iloc[range(n-min_time_rebalance,n)]["Stocks"].astype(float)) == 0:
            transactions.iloc[n]['Stocks'] == 1
        elif transactions.iloc[n]['Stocks'] == -1 and np.min(transactions.iloc[range(n-min_time_rebalance,n)]["Stocks"].astype(float)) == 0 and np.max(transactions.iloc[range(n-min_time_rebalance,n)]["Stocks"].astype(float)) == 0:
            transactions.iloc[n]['Stocks'] == -1    
        else:
            transactions.iloc[n]['Stocks'] = 0

        if transactions.iloc[n]['Bonds'] == 1 and np.min(transactions.iloc[range(n-min_time_rebalance,n)]["Bonds"].astype(float)) == 0 and np.max(transactions.iloc[range(n-min_time_rebalance,n)]["Bonds"].astype(float)) == 0:
            transactions.iloc[n]['Bonds'] == 1
        elif transactions.iloc[n]['Bonds'] == -1 and np.min(transactions.iloc[range(n-min_time_rebalance,n)]["Bonds"].astype(float)) == 0 and np.max(transactions.iloc[range(n-min_time_rebalance,n)]["Bonds"].astype(float)) == 0:
            transactions.iloc[n]['Bonds'] == -1    
        else:
            transactions.iloc[n]['Bonds'] = 0
          
    # Calculate the value of stocks / bonds traded
    # At first day, initialize portfolio
    if historicals.iloc[n]["Date"] == first_day_backtest: 
        portfolio.iloc[n]['Stocks'] = starting_value * starting_equity_share * (1 - eq_chrg)
        portfolio.iloc[n]['Bonds'] = starting_value * starting_bond_share * (1 - bond_chrg)
        portfolio.iloc[n]["Portfolio"] = portfolio.iloc[n]['Stocks'] + portfolio.iloc[n]['Bonds']
        transactions_values.iloc[n]['Stocks'] = 0
        transactions_values.iloc[n]['Bonds'] = 0 
    # In case of purchasing stocks, the value fo the trade is equal to:
    # Value of shares purchased(t) = Value of bonds(t-1) * Value of Bond Index(t) / Value of Bond Index(t-1) * Share of bonds traded * (1-bond charge) * (1-equity charge)
    # Value of bonds sold(t) = - Value of bonds(t-1) * Value of Bond Index(t) / Value of Bond Index(t-1) * Share of bonds traded * (1-bond charge)
    elif transactions.iloc[n]['Stocks'] == 1:
        transactions_values.iloc[n]['Stocks'] = portfolio.iloc[n-1]['Bonds'] * np.float(historicals.iloc[n]["TLT 20Y"]) / np.float(historicals.iloc[n-1]["TLT 20Y"]) * share_bond_sold_when_incr_stock * (1 - eq_chrg) * (1 - bond_chrg)
        transactions_values.iloc[n]['Bonds'] = -portfolio.iloc[n-1]['Bonds'] * np.float(historicals.iloc[n]["TLT 20Y"]) / np.float(historicals.iloc[n-1]["TLT 20Y"]) * share_bond_sold_when_incr_stock * (1 - bond_chrg)
    # In case of selling stocks, the value fo the trade is equal to:
    # Value of bonds purchased(t) = Value of stocks(t-1) * Value of Equity Index(t) / Value of Equity Index(t-1) * Share of stocks traded * (1-bond charge) * (1-equity charge)
    # Value of shares sold(t) = - Value of stocks(t-1) * Value of Equity Index(t) / Value of Equity Index(t-1) * Share of stocks traded * (1-equity charge)
    elif transactions.iloc[n]['Stocks'] == -1:
        transactions_values.iloc[n]['Stocks'] = -portfolio.iloc[n-1]['Stocks'] * np.float(historicals.iloc[n]["DOW JONES COMPOSITE"]) / np.float(historicals.iloc[n-1]["DOW JONES COMPOSITE"]) * share_bond_bought_when_decr_stock * (1 - eq_chrg) 
        transactions_values.iloc[n]['Bonds'] = portfolio.iloc[n-1]['Stocks'] * np.float(historicals.iloc[n]["DOW JONES COMPOSITE"]) / np.float(historicals.iloc[n-1]["DOW JONES COMPOSITE"]) * share_bond_bought_when_decr_stock * (1 - eq_chrg) * (1 - bond_chrg)
    # In case of selling bonds, the value fo the trade is equal to:
    # Value of bonds sold(t) = -Value of Bonds(t-1) * Value of Bond Index(t) / Value of Bond Index(t-1) * Share of bonds traded * (1-bond charge)
    # Value of shares purchased(t) = Value of Bonds(t-1) * Value of Bond Index(t) / Value of Bond Index(t-1) * Share of bonds traded * (1-bond charge) * (1-equity charge)
    elif transactions.iloc[n]['Bonds'] == -1:
        transactions_values.iloc[n]['Stocks'] = portfolio.iloc[n-1]['Bonds'] * np.float(historicals.iloc[n]["TLT 20Y"]) / np.float(historicals.iloc[n-1]["TLT 20Y"]) * share_bought_sold_when_decr_bond * (1 - eq_chrg) * (1 - bond_chrg)
        transactions_values.iloc[n]['Bonds'] = -portfolio.iloc[n-1]['Bonds'] * np.float(historicals.iloc[n]["TLT 20Y"]) / np.float(historicals.iloc[n-1]["TLT 20Y"]) * share_bought_sold_when_decr_bond * (1 - bond_chrg)               
    # In case of buying bonds, the value fo the trade is equal to:
    # Value of bonds bought(t) = Value of stocks(t-1) * Value of Equity Index(t) / Value of Equity Index(t-1) * Share of stocks traded * (1-bond charge) * (1-equity charge)
    # Value of shares purchased(t) = -Value of stocks(t-1) * Value of Equity Index(t) / Value of Equity Index(t-1) * Share of stocks traded * (1-equity charge)
    elif transactions.iloc[n]['Bonds'] == 1:
        transactions_values.iloc[n]['Stocks'] = -portfolio.iloc[n-1]['Stocks'] * np.float(historicals.iloc[n]["DOW JONES COMPOSITE"]) / np.float(historicals.iloc[n-1]["DOW JONES COMPOSITE"]) * share_stock_sold_when_incr_bond * (1 - eq_chrg) 
        transactions_values.iloc[n]['Bonds'] = portfolio.iloc[n-1]['Stocks'] * np.float(historicals.iloc[n]["DOW JONES COMPOSITE"]) / np.float(historicals.iloc[n-1]["DOW JONES COMPOSITE"]) * share_stock_sold_when_incr_bond * (1 - eq_chrg) * (1 - bond_chrg)       
    
    if historicals.iloc[n]["Date"] > first_day_backtest: 
        # Calculate the value of shares in portfolio (update the value of stocks from previous period and new transaction)
        portfolio.iloc[n]["Stocks"] = portfolio.iloc[n-1]["Stocks"] * np.float(historicals.iloc[n]["DOW JONES COMPOSITE"]) / np.float(historicals.iloc[n-1]["DOW JONES COMPOSITE"]) + transactions_values.iloc[n]['Stocks']
        # Calculate the value of bonds in portfolio (update the value of bonds from previous period and new transaction)
        portfolio.iloc[n]["Bonds"] = portfolio.iloc[n-1]["Bonds"] * np.float(historicals.iloc[n]["TLT 20Y"]) / np.float(historicals.iloc[n-1]["TLT 20Y"]) + transactions_values.iloc[n]['Bonds']
        # Total portfolio
        portfolio.iloc[n]["Portfolio"] = portfolio.iloc[n]["Stocks"] + portfolio.iloc[n]["Bonds"]
        
    print("n=", n)
    print("Stocks=", portfolio.iloc[n]["Stocks"])
    print("Bonds=", portfolio.iloc[n]["Bonds"])
    print("Portfolio=", portfolio.iloc[n]["Portfolio"])
    

# Plot historical portfolio
portfolio["Portfolio"].plot(kind='line')
plt.show()

# Plot DJ and TLT in one plot
fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('Date')
ax1.set_ylabel('Dow Jones', color=color)
ax1.plot(historicals["Date"], historicals["DOW JONES COMPOSITE"], color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx() # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('TLT', color=color)  # we already handled the x-label with ax1
ax2.plot(historicals["Date"], historicals["TLT 20Y"], color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout() # otherwise the right y-label is slightly clipped
plt.show()

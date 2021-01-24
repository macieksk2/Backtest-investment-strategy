# -*- coding: utf-8 -*-
"""
V2:
- Transfer most of the code from for loop to list comprehension

"""
# Import packages
import os
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import time

# CHECK TIME RUNNING
start_time = time.time()

# Change path
os.chdir(r"...\Investment strategy backtesting\v2")

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
share_stock_sold_when_decr_stock = 1.0
# Share of bonds sold when decreasing bonds position
share_bond_sold_when_decr_stock = 1.0
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
# Check if date is after the starting date
# Calculate short term MA - DJ
MA[(short_MA-1):]["DJ short"] = np.convolve(historicals["DOW JONES COMPOSITE"].astype(float), np.ones(short_MA)/short_MA, mode='valid')
# Calculate long term MA - DJ
MA[(long_MA-1):]["DJ long"] = np.convolve(historicals["DOW JONES COMPOSITE"].astype(float), np.ones(long_MA)/long_MA, mode='valid')
# Calculate short term MA - TLT
MA[(short_MA-1):]["Bond short"] = np.convolve(historicals["TLT 20Y"].astype(float), np.ones(short_MA)/short_MA, mode='valid')
# Calculate long term MA - TLT
MA[(long_MA-1):]["Bond long"] = np.convolve(historicals["TLT 20Y"].astype(float), np.ones(long_MA)/long_MA, mode='valid')
# Calculate DJ/TLT ratio, check whether stock price and TLT index are within the bounds
MA["DJ/TLT"] = np.array(historicals["DOW JONES COMPOSITE"] / historicals["TLT 20Y"])    

# Add to MA dataframe columns check if short term MA are above long term MA (DJ or Bond indices)
MA["DJ short > DJ long"] = MA[(long_MA-1):]["DJ short"] > MA[(long_MA-1):]["DJ long"]
MA["DJ short < DJ long"] = MA[(long_MA-1):]["DJ short"] < MA[(long_MA-1):]["DJ long"]
MA["Bond short > Bond long"] = MA[(long_MA-1):]["Bond short"] > MA[(long_MA-1):]["Bond long"]
MA["Bond short < Bond long"] = MA[(long_MA-1):]["Bond short"] < MA[(long_MA-1):]["Bond long"]

# Add to MA dataframe products of vectors with their lags
# 1 - TRUE
# else - FALSE
MA["DJ short > DJ long & DJ short.L1 < DJ long.L1"] = MA[(long_MA-1):]["DJ short > DJ long"] - MA[(long_MA-1):]["DJ short > DJ long"].shift(1)
MA["DJ short < DJ long & DJ short.L1 > DJ long.L1"] = MA[(long_MA-1):]["DJ short < DJ long"] - MA[(long_MA-1):]["DJ short < DJ long"].shift(1)
MA["Bond short > Bond long & Bond short.L1 < Bond long.L1"] = MA[(long_MA-1):]["Bond short > Bond long"] - MA[(long_MA-1):]["Bond short > Bond long"].shift(1)
MA["Bond short < Bond long & Bond short.L1 > Bond long.L1"] = MA[(long_MA-1):]["Bond short < Bond long"] - MA[(long_MA-1):]["Bond short < Bond long"].shift(1)

# Add to MA dataframe vector checking whether DJ/TLT crossed lower/upper bound in specific period
# -1 - TRUE
# else - FALSE
MA["DJ/TLT < lower bound"] = MA["DJ/TLT"] < lower_DJ_TLT * 100
MA["DJ/TLT > upper bound"] = MA["DJ/TLT"] < upper_DJ_TLT * 100
MA["DJ/TLT < lower limit & DJ/TLT.L1 > lower limit"] = MA[(long_MA-1):]["DJ/TLT < lower bound"] - MA[(long_MA-1):]["DJ/TLT < lower bound"].shift(1)
MA["DJ/TLT > upper limit & DJ/TLT.L1 < upper limit"] = MA[(long_MA-1):]["DJ/TLT > upper bound"] - MA[(long_MA-1):]["DJ/TLT > upper bound"].shift(1)

# Replace NaN with zeros
MA = MA.fillna(0)

# Has short term MA crossed long term MA?
# Has it crossed it from below? -> BUY MORE DJ
# Has DJ/TLT crossed lower bound? -> BUY MORE DJ
transactions['Stocks'] = [1.0 if MA.iloc[n]["DJ short > DJ long & DJ short.L1 < DJ long.L1"] == 1 or MA.iloc[n]["DJ/TLT < lower limit & DJ/TLT.L1 > lower limit"] == 1 else 0.0 for n in range(len(historicals))]
# Has it crossed it from above? -> SELL MORE DJ 
# Has DJ/TLT crossed upper bound? -> SELL MORE DJ 
transactions['Stocks'] = [-1.0 if MA.iloc[n]["DJ short < DJ long & DJ short.L1 > DJ long.L1"] == 1 or MA.iloc[n]["DJ/TLT > upper limit & DJ/TLT.L1 < upper limit"] == -1 else transactions.iloc[n]['Stocks'] for n in range(len(historicals)) ]
# Bonds
transactions['Bonds'] = [1.0 if MA.iloc[n]["Bond short > Bond long & Bond short.L1 < Bond long.L1"] == 1 else 0.0 for n in range(len(historicals)) ]
# Has it crossed it from above? -> SELL MORE TLT 
transactions['Bonds'] = [-1.0 if MA.iloc[n]["Bond short < Bond long & Bond short.L1 > Bond long.L1"] == 1 else transactions.iloc[n]['Bonds'] for n in range(len(historicals)) ]

# # If the transaction is to be done, check if enough time passed from the last trade
transactions['Stocks'] = [1.0 if transactions.iloc[n]['Stocks'] == 1 and np.min(transactions.iloc[range(n-min_time_rebalance,n)]["Stocks"].astype(float)) == 0 and np.max(transactions.iloc[range(n-min_time_rebalance,n)]["Stocks"].astype(float)) == 0 
                          else -1.0 if transactions.iloc[n]['Stocks'] == -1 and np.min(transactions.iloc[range(n-min_time_rebalance,n)]["Stocks"].astype(float)) == 0 and np.max(transactions.iloc[range(n-min_time_rebalance,n)]["Stocks"].astype(float)) == 0 
                          else 0.0 for n in range(len(historicals))]

transactions['Bonds'] = [1.0 if transactions.iloc[n]['Bonds'] == 1 and np.min(transactions.iloc[range(n-min_time_rebalance,n)]["Bonds"].astype(float)) == 0 and np.max(transactions.iloc[range(n-min_time_rebalance,n)]["Bonds"].astype(float)) == 0 
                          else -1.0 if transactions.iloc[n]['Bonds'] == -1 and np.min(transactions.iloc[range(n-min_time_rebalance,n)]["Bonds"].astype(float)) == 0 and np.max(transactions.iloc[range(n-min_time_rebalance,n)]["Bonds"].astype(float)) == 0 
                          else 0.0 for n in range(len(historicals))]

# Iterate through all historical dates
for n in range(len(historicals)):   
      
    # Calculate the value of stocks / bonds traded
    # At first day, initialize portfolio
    if historicals.iloc[n]["Date"] == first_day_backtest: 
        portfolio.iloc[n]['Stocks'] = starting_value * starting_equity_share * (1 - eq_chrg)
        portfolio.iloc[n]['Bonds'] = starting_value * starting_bond_share * (1 - bond_chrg)
        portfolio.iloc[n]["Portfolio"] = portfolio.iloc[n]['Stocks'] + portfolio.iloc[n]['Bonds']
        transactions_values.iloc[n]['Stocks'] = 0
        transactions_values.iloc[n]['Bonds'] = 0      
    elif transactions.iloc[n]['Stocks'] == 1:
        transactions_values.iloc[n]['Stocks'] = portfolio.iloc[n-1]['Bonds'] * np.float(historicals.iloc[n]["TLT 20Y"]) / np.float(historicals.iloc[n-1]["TLT 20Y"]) * share_bond_sold_when_incr_stock * (1 - eq_chrg) * (1 - bond_chrg)
        transactions_values.iloc[n]['Bonds'] = -portfolio.iloc[n-1]['Bonds'] * np.float(historicals.iloc[n]["TLT 20Y"]) / np.float(historicals.iloc[n-1]["TLT 20Y"]) * share_bond_sold_when_incr_stock * (1 - bond_chrg)
    elif transactions.iloc[n]['Stocks'] == -1:
        transactions_values.iloc[n]['Stocks'] = -portfolio.iloc[n-1]['Stocks'] * np.float(historicals.iloc[n]["DOW JONES COMPOSITE"]) / np.float(historicals.iloc[n-1]["DOW JONES COMPOSITE"]) * share_bond_sold_when_decr_stock * (1 - eq_chrg) 
        transactions_values.iloc[n]['Bonds'] = portfolio.iloc[n-1]['Stocks'] * np.float(historicals.iloc[n]["DOW JONES COMPOSITE"]) / np.float(historicals.iloc[n-1]["DOW JONES COMPOSITE"]) * share_bond_sold_when_decr_stock * (1 - eq_chrg) * (1 - bond_chrg)
    elif transactions.iloc[n]['Bonds'] == -1:
        transactions_values.iloc[n]['Stocks'] = portfolio.iloc[n-1]['Bonds'] * np.float(historicals.iloc[n]["TLT 20Y"]) / np.float(historicals.iloc[n-1]["TLT 20Y"]) * share_stock_sold_when_decr_stock * (1 - eq_chrg) * (1 - bond_chrg)
        transactions_values.iloc[n]['Bonds'] = -portfolio.iloc[n-1]['Bonds'] * np.float(historicals.iloc[n]["TLT 20Y"]) / np.float(historicals.iloc[n-1]["TLT 20Y"]) * share_stock_sold_when_decr_stock * (1 - bond_chrg)               
    elif transactions.iloc[n]['Bonds'] == 1:
        transactions_values.iloc[n]['Stocks'] = -portfolio.iloc[n-1]['Stocks'] * np.float(historicals.iloc[n]["DOW JONES COMPOSITE"]) / np.float(historicals.iloc[n-1]["DOW JONES COMPOSITE"]) * share_stock_sold_when_incr_bond * (1 - eq_chrg) 
        transactions_values.iloc[n]['Bonds'] = portfolio.iloc[n-1]['Stocks'] * np.float(historicals.iloc[n]["DOW JONES COMPOSITE"]) / np.float(historicals.iloc[n-1]["DOW JONES COMPOSITE"]) * share_stock_sold_when_incr_bond * (1 - eq_chrg) * (1 - bond_chrg)       
    
    if historicals.iloc[n]["Date"] > first_day_backtest: 
        # Calculate the value of shares in portfolio
        portfolio.iloc[n]["Stocks"] = portfolio.iloc[n-1]["Stocks"] * np.float(historicals.iloc[n]["DOW JONES COMPOSITE"]) / np.float(historicals.iloc[n-1]["DOW JONES COMPOSITE"]) + transactions_values.iloc[n]['Stocks']
        # Calculate the value of bnods in portfolio
        portfolio.iloc[n]["Bonds"] = portfolio.iloc[n-1]["Bonds"] * np.float(historicals.iloc[n]["TLT 20Y"]) / np.float(historicals.iloc[n-1]["TLT 20Y"]) + transactions_values.iloc[n]['Bonds']
        # Total portfolio
        portfolio.iloc[n]["Portfolio"] = portfolio.iloc[n]["Stocks"] + portfolio.iloc[n]["Bonds"]
        
    print("n=", n)
    print("Stocks=", portfolio.iloc[n]["Stocks"])
    print("Bonds=", portfolio.iloc[n]["Bonds"])
    print("Portfolio=", portfolio.iloc[n]["Portfolio"])
# OUTPUT TIME RUNNING
print("--- %s seconds ---" % (time.time() - start_time))

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

# Save variables to file
file = open("dump_transactions.txt", "w")
pd.set_option('display.max_rows', len(transactions))
file.write(str(transactions))
file.close()

file = open("dump_transactions_values.txt", "w")
pd.set_option('display.max_rows', len(transactions_values))
file.write(str(transactions_values))
file.close()

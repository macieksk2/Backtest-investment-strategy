# -*- coding: utf-8 -*-
"""
V3:
- Move most of the calculations to newly defined functions (file investment_backtesting_functions.py)
- Create plots of Portfolio evolution, changes between Stocks and Bonds allocaiton, comaprison of evolution of Dowj Jones Index and TLT 20Y fund

@author: maciej_sliz
"""
# Import packages
import os
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import time

# Start timing
start_time = time.time()

# Change path
os.chdir(r"...\Investment strategy backtesting\v3")

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
# INITIALIZATION:
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

########################################################################
# FUNCTIONS:
########################################################################
from investment_backtesting_functions import *

########################################################################
# CALCULATION:
########################################################################
    
# Check if date is after the starting date
# Calculate short term MA - DJ
MA[(short_MA-1):]["DJ short"] = moving_average(historicals["DOW JONES COMPOSITE"], short_MA, float)
# Calculate long term MA - DJ
MA[(long_MA-1):]["DJ long"] = moving_average(historicals["DOW JONES COMPOSITE"], long_MA, float)
# Calculate short term MA - TLT
MA[(short_MA-1):]["Bond short"] = moving_average(historicals["TLT 20Y"], short_MA, float)
# Calculate long term MA - TLT
MA[(long_MA-1):]["Bond long"] = moving_average(historicals["TLT 20Y"], long_MA, float)
# Calculate DJ/TLT ratio, check whether stock price and TLT index are within the bounds
MA["DJ/TLT"] = np.array(historicals["DOW JONES COMPOSITE"] / historicals["TLT 20Y"])    

# Add to MA dataframe columns checking if short term MA is above long term MA (DJ or Bond indices)
MA["DJ short > DJ long"] = compare_series(MA,"DJ short","DJ long", long_MA, ">", flag = 1)
MA["DJ short < DJ long"] = compare_series(MA,"DJ short","DJ long", long_MA, "<", flag = 1)
MA["Bond short > Bond long"] = compare_series(MA,"Bond short","Bond long", long_MA, ">", flag = 1)
MA["Bond short < Bond long"] = compare_series(MA,"Bond short","Bond long", long_MA, "<", flag = 1)

# Add to MA dataframe differences of vectors with their lags
# 1 - TRUE
# else - FALSE
MA["DJ short > DJ long & DJ short.L1 < DJ long.L1"] = series_difference(MA, "DJ short > DJ long", long_MA, 1) 
MA["DJ short < DJ long & DJ short.L1 > DJ long.L1"] = series_difference(MA, "DJ short < DJ long", long_MA, 1) 
MA["Bond short > Bond long & Bond short.L1 < Bond long.L1"] = series_difference(MA, "Bond short > Bond long", long_MA, 1) 
MA["Bond short < Bond long & Bond short.L1 > Bond long.L1"] = series_difference(MA, "Bond short < Bond long", long_MA, 1)

# Add to MA dataframe vector checking whether DJ/TLT crossed lower/upper bound in specific period
# -1 - TRUE
# else - FALSE
MA["DJ/TLT < lower bound"] = compare_series(MA,"DJ/TLT", sign = "<", flag = 2, constant_val = lower_DJ_TLT * 100)
MA["DJ/TLT > upper bound"] = compare_series(MA,"DJ/TLT", sign = "<", flag = 2, constant_val = upper_DJ_TLT * 100)
MA["DJ/TLT < lower limit & DJ/TLT.L1 > lower limit"] = series_difference(MA, "DJ/TLT < lower bound", long_MA, 1)
MA["DJ/TLT > upper limit & DJ/TLT.L1 < upper limit"] = series_difference(MA, "DJ/TLT > upper bound", long_MA, 1)

# Replace NaN with zeros
MA = MA.fillna(0)

# Has short term MA crossed long term MA?
# Has it crossed it from below? -> BUY MORE DJ
# Has DJ/TLT crossed lower bound? -> BUY MORE DJ
# Has it crossed it from above? -> SELL MORE DJ 
# Has DJ/TLT crossed upper bound? -> SELL MORE DJ 
transactions['Stocks'] = transaction(MA, "Stocks", 
                                     buy_col_name_1 = "DJ short > DJ long & DJ short.L1 < DJ long.L1", 
                                     buy_col_name_2 = "DJ/TLT < lower limit & DJ/TLT.L1 > lower limit", 
                                     sell_col_name_1 ="DJ short < DJ long & DJ short.L1 > DJ long.L1", 
                                     sell_col_name_2 = "DJ/TLT > upper limit & DJ/TLT.L1 < upper limit") 
# Bonds
# Has it crossed it from below? -> BUY MORE TLT
# Has it crossed it from above? -> SELL MORE TLT 
transactions['Bonds'] = transaction(MA, "Bonds", 
                                    buy_col_name_1 = "Bond short > Bond long & Bond short.L1 < Bond long.L1", 
                                    sell_col_name_1 = "Bond short < Bond long & Bond short.L1 > Bond long.L1")

# # If the transaction is to be done, check if enough time passed from the last trade
transactions['Stocks'] = check_time_passed(transactions, "Stocks", min_time = min_time_rebalance)
transactions['Bonds'] = check_time_passed(transactions, "Bonds", min_time = min_time_rebalance)

# Iterate through all historical dates
for n in range(len(historicals)):   
      
    # Calculate the value of stocks / No documbonds traded
    # At first day, initialize portfolio
    if historicals.iloc[n]["Date"] == first_day_backtest: 
        portfolio.iloc[n]['Stocks'] = starting_value * starting_equity_share * (1 - eq_chrg)
        portfolio.iloc[n]['Bonds'] = starting_value * starting_bond_share * (1 - bond_chrg)
        portfolio.iloc[n]["Portfolio"] = portfolio.iloc[n]['Stocks'] + portfolio.iloc[n]['Bonds']
        transactions_values.iloc[n]['Stocks'] = 0
        transactions_values.iloc[n]['Bonds'] = 0      
    elif transactions.iloc[n]['Stocks'] == 1:
        transactions_values.iloc[n]['Stocks'] = value_asset(portfolio, historicals, n, "Bonds", "TLT 20Y") * share_bond_sold_when_incr_stock * (1 - eq_chrg) * (1 - bond_chrg)
        transactions_values.iloc[n]['Bonds'] = -value_asset(portfolio, historicals, n, "Bonds", "TLT 20Y") * share_bond_sold_when_incr_stock * (1 - bond_chrg)
    elif transactions.iloc[n]['Stocks'] == -1:
        transactions_values.iloc[n]['Stocks'] = -value_asset(portfolio, historicals, n, "Stocks", "DOW JONES COMPOSITE") * share_bond_sold_when_decr_stock * (1 - eq_chrg) 
        transactions_values.iloc[n]['Bonds'] = value_asset(portfolio, historicals, n, "Stocks", "DOW JONES COMPOSITE") * share_bond_sold_when_decr_stock * (1 - eq_chrg) * (1 - bond_chrg)
    elif transactions.iloc[n]['Bonds'] == -1:
        transactions_values.iloc[n]['Stocks'] = value_asset(portfolio, historicals, n, "Bonds", "TLT 20Y") * share_stock_sold_when_decr_stock * (1 - eq_chrg) * (1 - bond_chrg)
        transactions_values.iloc[n]['Bonds'] = -value_asset(portfolio, historicals, n, "Bonds", "TLT 20Y") * share_stock_sold_when_decr_stock * (1 - bond_chrg)               
    elif transactions.iloc[n]['Bonds'] == 1:
        transactions_values.iloc[n]['Stocks'] = -value_asset(portfolio, historicals, n, "Stocks", "DOW JONES COMPOSITE") * share_stock_sold_when_incr_bond * (1 - eq_chrg) 
        transactions_values.iloc[n]['Bonds'] = value_asset(portfolio, historicals, n, "Stocks", "DOW JONES COMPOSITE") * share_stock_sold_when_incr_bond * (1 - eq_chrg) * (1 - bond_chrg)       
    
    if historicals.iloc[n]["Date"] > first_day_backtest: 
        # Calculate the value of shares in portfolio
        portfolio.iloc[n]["Stocks"] = value_asset(portfolio, historicals, n, "Stocks", "DOW JONES COMPOSITE") + transactions_values.iloc[n]['Stocks']
        # Calculate the value of bnods in portfolio
        portfolio.iloc[n]["Bonds"] = value_asset(portfolio, historicals, n, "Bonds", "TLT 20Y") + transactions_values.iloc[n]['Bonds']
        # Total portfolio
        portfolio.iloc[n]["Portfolio"] = portfolio.iloc[n]["Stocks"] + portfolio.iloc[n]["Bonds"]
        
    print("n=", n)
    print("Stocks=", portfolio.iloc[n]["Stocks"])
    print("Bonds=", portfolio.iloc[n]["Bonds"])
    print("Portfolio=", portfolio.iloc[n]["Portfolio"])
# OUTPUT TIME RUNNING
print("--- %s seconds ---" % (time.time() - start_time))

########################################################################
# PLOTTING:
########################################################################

# Plot historical portfolio
portfolio["Portfolio"].plot(kind='line')
portfolio["Stocks"].plot(kind='line')
portfolio["Bonds"].plot(kind='line')
plt.legend(['Portfolio', 'Stocks', 'Bonds']);
plt.show()

# Plot the transactions in time
transactions["Stocks"].plot(kind='line')
transactions["Bonds"].plot(kind='line')
plt.legend(['Stocks', 'Bonds']);
plt.show()

# Plot the transactions values in time
transactions_values["Stocks"].plot(kind='line')
transactions_values["Bonds"].plot(kind='line')
plt.legend(['Stocks', 'Bonds']);
plt.show()

# Plot the DJ vs TLT (normalized) in one plot
rescaled_DJ =  (historicals["DOW JONES COMPOSITE"] - np.mean(historicals["DOW JONES COMPOSITE"])) / np.std(historicals["DOW JONES COMPOSITE"])
rescaled_TLT = (historicals["TLT 20Y"] - np.mean(historicals["TLT 20Y"])) / np.std(historicals["TLT 20Y"])

rescaled_DJ.plot(kind='line')
rescaled_TLT.plot(kind='line')
plt.legend(['DJ', 'TLT 20Y']);
plt.show()

########################################################################
# VALIDATION:
########################################################################

# Save variables to file
file = open("dump_transactions.txt", "w")
pd.set_option('display.max_rows', len(transactions))
file.write(str(transactions))
file.close()

file = open("dump_transactions_values.txt", "w")
pd.set_option('display.max_rows', len(transactions_values))
file.write(str(transactions_values))
file.close()

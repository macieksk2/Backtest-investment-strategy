# -*- coding: utf-8 -*-
"""
Function used in the main backtesting code

@author: maciej_sliz
"""
# Import packages
import pandas as pd
import numpy as np

########################################################################
# FUNCTIONS:
########################################################################

def moving_average(input_data, ma_len = 30, type_series = float):
    """
    Calculate moving average based on time series in pandas DataFrame object using numpy convolve function
    
    Input:
        - input_data - input DataFrame with historical time series (one column)
        - ma_len - the length of moving average window (in days)
   
    """
    out = np.convolve(input_data.astype(type_series), np.ones(ma_len)/ma_len, mode='valid')
    
    return out

def compare_series(input_data, col_name_1 = "col_name_1", col_name_2 = "col_name_2", ma_len = 200, sign = "<", flag = 1, constant_val = 0):
    """
    flag == 1:
        Check whether elements of one series are above or below the corresponding elements of another series
    flag == 2:
        Compare series with constant
    
    Input:
        - input_data - input
        - col_name_1 - input series name 1
        - col_name_2 - input series name 2
        - ma_len - length of MA window
        - sign - check if the first series is lower ("<") or higher (">")
        - constant_val - if flag == 2, comapre against this constant value
    """
    if flag == 1:
        if sign == "<":
            out = input_data[(ma_len-1):][col_name_1] < input_data[(ma_len-1):][col_name_2]
        else:
            out = input_data[(ma_len-1):][col_name_1] > input_data[(ma_len-1):][col_name_2]
    else:
        if sign == "<":
            out = input_data[col_name_1] < constant_val
        else:
            out = input_data[col_name_1] > constant_val
            
    return out

def series_difference(input_data, col_name, ma_len = 200, lag_order = 1):
    """
    Calculate the difference of series with its lag
    
    Input:
        - input_data - input
        - col_name - input series name
        - ma_len - length of MA window
        - lag_order - order of lagging the series (in days)
   
    """
    out = input_data[(ma_len-1):][col_name] - input_data[(ma_len-1):][col_name].shift(lag_order)
    
    return out


def transaction(input_data, asset_name, buy_col_name_1 = "x", buy_col_name_2 = "x", sell_col_name_1 = "x", sell_col_name_2 = "x"):
    """
    Check if the transaction should be: buy, sell or no transactions based on the relationship of moveing averages and Equity-to-Bond ratio
    
    Input:
        - input_data - input
        - asset_name - Stocks or Bonds currently
        - buy_col_name_1 - first condition for BUY transaction
        - buy_col_name_2 - second condition for BUY transaction
        - sell_col_name_1 - first condition for SELL transaction
        - sell_col_name_2 - second condition for SELL transaction
        
    Output:
        -  1.0 - BUY
        - -1.0 - SELL
        -  0.0 - nothing
   
    """
    if asset_name == "Stocks":
        out = [1.0 if input_data.iloc[n][buy_col_name_1] == 1 or input_data.iloc[n][buy_col_name_2] == 1 
               else -1.0 if input_data.iloc[n][sell_col_name_1] == 1 or input_data.iloc[n][sell_col_name_2] == -1
               else 0.0 for n in range(len(input_data))]
    else:
        out = [1.0 if input_data.iloc[n][buy_col_name_1] == 1
               else -1.0 if input_data.iloc[n][sell_col_name_1] == 1
               else 0.0 for n in range(len(input_data))]
    
    return out

def check_time_passed(input_data, asset_name, min_time = 30):
    
    """
    Check if enough time passed from last transaction to proceed with the next one
    Input:
        - input_data - input
        - asset_name - Stocks or Bonds currently
        - min_time - minimum number of days passed from last trade

    """
    out = [1.0 if input_data.iloc[n][asset_name] == 1 and np.min(input_data.iloc[range(n-min_time,n)][asset_name].astype(float)) == 0 and np.max(input_data.iloc[range(n-min_time,n)][asset_name].astype(float)) == 0 
                          else -1.0 if input_data.iloc[n][asset_name] == -1 and np.min(input_data.iloc[range(n-min_time,n)][asset_name].astype(float)) == 0 and np.max(input_data.iloc[range(n-min_time,n)][asset_name].astype(float)) == 0 
                          else 0.0 for n in range(len(input_data))]
    
    return out

def value_asset(portfolio_data, hist_vals, time_idx, asset_name, col_name):
    """
    Update value of the assets (Stocks, Bonds from the previous period) by the daily change in index value
    
    Input:
        - portfolio_data - value of portfolio's Stocks and Bonds in time
        - hist_vals - historical series of Stocks and Bonds
        - asset_name - Stocks or Bonds currently
        - col_name - name of the column of historical series of the Stocks or Bonds index
    
    """
    out = portfolio_data.iloc[time_idx-1][asset_name] * np.float(hist_vals.iloc[time_idx][col_name]) / np.float(hist_vals.iloc[time_idx-1][col_name])
    
    return out


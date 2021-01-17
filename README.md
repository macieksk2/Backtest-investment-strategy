# Backtest-investment-strategy
Python script backtesting the investment strategy based on investment in Dow Jones Composite Index and 20Y US Treasuries

The strategy is based on transfering the funds between equity and bonds indices based on crossovers of short- and longer term moving averages of both:
- When short-term Moving Average crosses the long-term MA from the bottom, it is treated as buying signal. When it occurs in case of DJ, a portion of shares in bond fund are sold to increase equity position. The same applies to bonds.
- When short-term Moving Average declines below the long-term MA, it is treated as selling signal. When it occurs in case of DJ, a portion of shares in equity fund are sold to increase bond position. The same applies to bonds.
- The last part of the strategy is based on the level of Dow Jones to TLT 20Y ratio. When it rises above upper level, it is a sign that equities are overvalued comapred to bonds and, again, a part of them are sold to increase bond position. ON the contrary, a decline below parametrized lower bound is treated as a signal to increase share of equities since they are relatively undervalued to bonds.

The code includes parameters to alter the strategy, i.e.:
# Starting Value = 100000
# Share of equities initially = 0.8
# Share of bonds intitally = 0.2

# Charge for purchasing Equity = 0.003
# Charge for purchasingBond = 0.002
# Min time between rebalances (in trading days) = 30
# Share of bonds sold when increasing stocks position = 1.0
# Share of stocks sold when increasing bonds position = 0.0
# Share of stocks sold when decreasing stocks position = 1.0
# Share of bonds sold when decreasing bonds position = 1.0
# Shorter term MA window (in trading days) = 30
# Longer term MA window (in trading days) = 200
# Upper bound of DJ/TLT ratio = 0.7
# Lower bound of DJ/TLT ratio = 0.4


# src/analysis/robustness_checks.py

import pandas as pd
from src.analysis.momentum_strategy_backtest import momentum_strategy
from src.analysis.summarize_performance import summarize_performance
from src.visualization.plotRobustnessChecks import plotRobustnessChecks
from src.visualization.plotPerformance import plot_cumulative_returns

def run_holding_period_check(price_data_daily, lookback_period, nLong, rf_monthly, spi_XsReturns_monthly, visualization_path):
    rc_holding_period = pd.DataFrame(index=range(1, 13), columns=['Sharpe_Ratio'])
    for i in range(1, 13):
        excess_returns_temp, _, _, _ = momentum_strategy(
            price_data_daily=price_data_daily,
            lookback_period=lookback_period,
            nLong=nLong,
            nShort=0,
            holding_period=i,
            rf_monthly=rf_monthly,
            trx_cost=0
        )
        excess_returns_temp.columns = ['Strategy_Returns']
        stats_temp = summarize_performance(excess_returns_temp, rf_monthly, spi_XsReturns_monthly, 12)
        rc_holding_period.loc[i, 'Sharpe_Ratio'] = stats_temp['Sharpe_Ratio_Arithmetic']['xs_Return']

    print("RC of Holding Period")
    print(rc_holding_period)

    plotRobustnessChecks(
        rc_holding_period,
        label="Long Only Strategy",
        title='Sharpe Ratios over Holding Periods',
        x_label='Holding Period',
        y_label='Sharpe Ratio',
        savefig=True,
        filename=visualization_path / 'rc_holding_period.png'
    )

def run_lookback_period_check(price_data_daily, lookback_period_range, nLong, nShort, holding_period, rf_monthly, spi_XsReturns_monthly, visualization_path):
    rc_lookback_period = pd.DataFrame(index=lookback_period_range, columns=['Sharpe_Ratio'])
    for i in lookback_period_range:
        excess_returns_temp, _, _, _ = momentum_strategy(
            price_data_daily=price_data_daily,
            lookback_period=i,
            nLong=nLong,
            nShort=nShort,
            holding_period=holding_period,
            rf_monthly=rf_monthly,
            trx_cost=0
        )
        excess_returns_temp.columns = ['Strategy_Returns']
        stats_temp = summarize_performance(excess_returns_temp, rf_monthly, spi_XsReturns_monthly, 12)
        rc_lookback_period.loc[i, 'Sharpe_Ratio'] = stats_temp['Sharpe_Ratio_Arithmetic']['xs_Return']

    print("RC of Lookback Period")
    print(rc_lookback_period)

    plotRobustnessChecks(
        rc_lookback_period,
        label="Long Only Strategy",
        title='Sharpe Ratios over Lookback Periods',
        x_label='Lookback Period',
        y_label='Sharpe Ratio',
        savefig=True,
        filename=visualization_path / 'rc_lookback_period.png'
    )

def run_number_assets_check(price_data_daily, lookback_period, nLong_range, nShort, holding_period, rf_monthly, spi_XsReturns_monthly, visualization_path):
    rc_number_assets = pd.DataFrame(index=nLong_range, columns=['Sharpe_Ratio'])
    for i in nLong_range:
        excess_returns_temp, _, _, _ = momentum_strategy(
            price_data_daily=price_data_daily,
            lookback_period=lookback_period,
            nLong=i,
            nShort=nShort,
            holding_period=holding_period,
            rf_monthly=rf_monthly,
            trx_cost=0
        )
        excess_returns_temp.columns = ['Strategy_Returns']
        stats_temp = summarize_performance(excess_returns_temp, rf_monthly, spi_XsReturns_monthly, 12)
        rc_number_assets.loc[i, 'Sharpe_Ratio'] = stats_temp['Sharpe_Ratio_Arithmetic']['xs_Return']

    print("RC of Number Assets")
    print(rc_number_assets)

    plotRobustnessChecks(
        rc_number_assets,
        label="Long Only Strategy",
        title='Sharpe Ratios over Number Assets Long',
        x_label='Number Assets Long',
        y_label='Sharpe Ratio',
        savefig=True,
        filename=visualization_path / 'rc_number_assets.png'
    )

def run_trx_cost_check(price_data_daily, lookback_period, nLong, nShort, holding_period, rf_monthly, spi_returns_monthly, visualization_path):
    rc_trxCost_return = pd.DataFrame()
    trx_costs = [0.001, 0.005, 0.01]
    labels = {
        'Strategy_Returns': 'Long Only Strategy',
        'Benchmark': 'SPI',
        'Portfolio_Returns': 'Long Only Strategy',
        'xs_Return': 'Long Only Strategy',
        'trx_cost_0.001': 'Long Only with Trx Cost: 0.1%',
        'trx_cost_0.005': 'Long Only with Trx Cost: 0.5%',
        'trx_cost_0.01': 'Long Only with Trx Cost: 1.0%',
    }

    # Initialize with base strategy returns
    _, _, _, portfolio_returns_longOnly = momentum_strategy(
        price_data_daily=price_data_daily,
        lookback_period=lookback_period,
        nLong=nLong,
        nShort=nShort,
        holding_period=holding_period,
        rf_monthly=rf_monthly,
        trx_cost=0
    )
    if isinstance(portfolio_returns_longOnly, pd.Series):
        portfolio_returns_longOnly = portfolio_returns_longOnly.to_frame()
    portfolio_returns_longOnly.columns = ['Strategy_Returns']
    rc_trxCost_return = portfolio_returns_longOnly.copy()

    for trx in trx_costs:
        _, _, _, portfolio_returns_temp = momentum_strategy(
            price_data_daily=price_data_daily,
            lookback_period=lookback_period,
            nLong=nLong,
            nShort=nShort,
            holding_period=holding_period,
            rf_monthly=rf_monthly,
            trx_cost=trx
        )
        if isinstance(portfolio_returns_temp, pd.Series):
            portfolio_returns_temp = portfolio_returns_temp.to_frame()
        portfolio_returns_temp.columns = [f'trx_cost_{trx}']
        rc_trxCost_return = pd.concat([rc_trxCost_return, portfolio_returns_temp], axis=1)

    plot_cumulative_returns(
        rc_trxCost_return,
        spi_returns_monthly,
        labels,
        title='Robustness Check Transaction Costs',
        x_label='Date',
        y_label='Cumulative Returns',
        figsize=(12, 6),
        grid=True,
        savefig=True,
        filename=visualization_path / 'rc_trxCost.png'
    )

    print("RC of Transaction Costs")
    print(rc_trxCost_return)

import pandas as pd
from src.analysis.momentum_strategy_backtest import momentum_strategy
from src.analysis.summarize_performance import summarize_performance, save_summary_to_latex

def run_robustness_checks(price_data_daily, rf_monthly, spi_XsReturns_monthly, visualization_path, strategy_params):
    """
    Run robustness checks for holding periods, lookback periods, and number of assets.

    Args:
        price_data_daily (pd.DataFrame): Daily price data for assets.
        rf_monthly (pd.DataFrame): Risk-free monthly returns.
        spi_XsReturns_monthly (pd.DataFrame): SPI excess returns over the risk-free rate.
        visualization_path (Path): Path to save robustness check plots.
        strategy_params (dict): Strategy parameters for lookback, holding period, and transaction costs.
    """
    lookback_period = strategy_params['lookback_period']
    holding_period = strategy_params['holding_period']
    trx_cost = strategy_params['trx_cost']

    # 1. Robustness over Holding Periods
    rc_holding_period = pd.DataFrame(index=range(1, 13), columns=['Sharpe_Ratio'])
    for i in range(1, 13):
        excess_returns, _, _, _ = momentum_strategy(
            price_data_daily, lookback_period, strategy_params['nLong'], strategy_params['nShort'], i, rf_monthly, trx_cost
        )
        excess_returns.columns = ['Strategy_Returns']
        stats_temp = summarize_performance(excess_returns, rf_monthly, spi_XsReturns_monthly, 12)
        rc_holding_period.loc[i, 'Sharpe_Ratio'] = stats_temp['Sharpe_Ratio_Arithmetic']['xs_Return']
    plotRobustnessChecks(
        rc_holding_period,
        title='Sharpe Ratios over Holding Periods',
        x_label='Holding Period',
        y_label='Sharpe Ratio',
        savefig=True,
        filename=visualization_path / 'rc_holding_period.png'
    )

    # 2. Robustness over Lookback Periods
    rc_lookback_period = pd.DataFrame(index=range(1, 13), columns=['Sharpe_Ratio'])
    for i in range(1, 13):
        excess_returns, _, _, _ = momentum_strategy(
            price_data_daily, i, strategy_params['nLong'], strategy_params['nShort'], holding_period, rf_monthly, trx_cost
        )
        excess_returns.columns = ['Strategy_Returns']
        stats_temp = summarize_performance(excess_returns, rf_monthly, spi_XsReturns_monthly, 12)
        rc_lookback_period.loc[i, 'Sharpe_Ratio'] = stats_temp['Sharpe_Ratio_Arithmetic']['xs_Return']
    plotRobustnessChecks(
        rc_lookback_period,
        title='Sharpe Ratios over Lookback Periods',
        x_label='Lookback Period',
        y_label='Sharpe Ratio',
        savefig=True,
        filename=visualization_path / 'rc_lookback_period.png'
    )

    # 3. Robustness over Number of Assets
    rc_number_assets = pd.DataFrame(index=range(5, 51), columns=['Sharpe_Ratio'])
    for i in range(5, 51):
        excess_returns, _, _, _ = momentum_strategy(
            price_data_daily, lookback_period, i, i, holding_period, rf_monthly, trx_cost
        )
        excess_returns.columns = ['Strategy_Returns']
        stats_temp = summarize_performance(excess_returns, rf_monthly, spi_XsReturns_monthly, 12)
        rc_number_assets.loc[i, 'Sharpe_Ratio'] = stats_temp['Sharpe_Ratio_Arithmetic']['xs_Return']
    plotRobustnessChecks(
        rc_number_assets,
        title='Sharpe Ratios over Number Assets Long/Short',
        x_label='Number of Assets',
        y_label='Sharpe Ratio',
        savefig=True,
        filename=visualization_path / 'rc_number_assets.png'
    )

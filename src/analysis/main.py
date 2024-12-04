# Import libraries
import pandas as pd
import numpy as np
import seaborn as sns
from pathlib import Path
from load_data import load_data
import sys

# Add the project root directory to sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# Load other funcitons
from src.visualization.plotPerformance import plot_cumulative_returns
from src.visualization.plotRobustnessChecks import plotRobustnessChecks
from summarize_performance import summarize_performance, save_summary_to_latex
from momentum_strategy_backtest import momentum_strategy


def main():
    # Define the base path for file locations
    base_path = Path(__file__).resolve().parents[2]

    # Construct file paths dynamically
    constituents_data_path = base_path / "data" / "processed" / "constituents_data.csv"
    rf_monthly_path = base_path / "data" / "processed" / "risk_free.csv"
    results_path = base_path / "data" / "results"
    spi_path = base_path / "data" / "processed" / "index_data.csv"
    summary_file_path_longOnly = results_path / "summary_performance_longOnly.tex"
    summary_file_path_longShort = results_path / "summary_performance_longShort.tex"
    visualization_path = base_path / "reports" / "figures"

    # Debug: Print the constructed file paths
    print(f"Constituent Data Path: {constituents_data_path}")
    print(f"Risk-Free Monthly Returns Path: {rf_monthly_path}")
    print(f"Results Path: {results_path}")

    # Ensure the results directory exists
    # results_path.mkdir(parents=True, exist_ok=True)

    # Load risk-free monthly returns
    rf_monthly = load_data(rf_monthly_path)
    print("Loaded risk-free monthly returns:")

    # Strategy parameters
    lookback_period = 6  # Number of months to look back
    nLong = 20             # Number of assets to go long
    nShort = 20            # Number of assets to short
    holding_period = 6    # Rebalance every month
    
    price_data_daily = load_data(constituents_data_path)
    
    # read spi index data
    spi_price_daily = load_data(spi_path)
    
    # Resample data to monthly frequency and calculate returns
    spi_price_monthly = spi_price_daily.resample('M').last()
    
    # Calculate Returns
    spi_returns_monthly = spi_price_monthly.pct_change()
    if isinstance(spi_returns_monthly, pd.Series):
        spi_returns_monthly = spi_returns_monthly.to_frame()
     
    # Avoid massive outliers
    spi_returns_monthly = np.clip(spi_returns_monthly, -0.5, 0.5)
    spi_XsReturns_monthly = spi_returns_monthly['SWISS PERFORMANCE INDEX - TOT RETURN IND'] - rf_monthly['monthly_return']
    if isinstance(spi_XsReturns_monthly, pd.Series):
        spi_XsReturns_monthly = spi_XsReturns_monthly.to_frame()
    
    # Rename Coluns for consistency
    spi_XsReturns_monthly.columns = ['Benchmark']
    spi_returns_monthly.columns = ['Benchmark']
    
    # ----- Run Backtest LONGONLY -----
    excess_returns_longOnly, portfolio_weights_longOnly, turnover_series_longOnly, portfolio_returns_longOnly = momentum_strategy(
        price_data_daily=price_data_daily,
        lookback_period=lookback_period,
        nLong=nLong,
        nShort=0,
        holding_period=holding_period,
        rf_monthly=rf_monthly,
        trx_cost=0
    )
    excess_returns_longOnly.columns = ['Xs Returns LongOnly']
    portfolio_returns_longOnly.columns = ['Returns LongOnly']
    
    # Save results
    excess_returns_longOnly.to_csv(results_path / "excess_returns_longOnly.csv", index=True, header=True)
    portfolio_weights_longOnly.to_csv(results_path / "portfolio_weights_longOnly.csv", index=True, header=True)
    turnover_series_longOnly.to_csv(results_path / "turnover_series_longOnly.csv", index=True, header=True)
    stats_longOnly = summarize_performance(excess_returns_longOnly, rf_monthly, spi_XsReturns_monthly, 12)
    save_summary_to_latex(stats_longOnly, summary_file_path_longOnly)
    # -----
    
    # ----- Run Backtest LONG / SHORT -----
    excess_returns_longShort, portfolio_weights_longShort, turnover_series_longShort, portfolio_returns_longShort = momentum_strategy(
        price_data_daily=price_data_daily,
        lookback_period=lookback_period,
        nLong=nLong,
        nShort=nShort,
        holding_period=holding_period,
        rf_monthly=rf_monthly,
        trx_cost=0
    )
    excess_returns_longShort.columns = ['Xs Returns LongShort']
    portfolio_returns_longShort.columns = ['Returns LongShort']
    
    # Save results
    excess_returns_longShort.to_csv(results_path / "excess_returns_longShort.csv", index=True, header=True)
    portfolio_weights_longShort.to_csv(results_path / "portfolio_weights_longShort.csv", index=True, header=True)
    turnover_series_longShort.to_csv(results_path / "turnover_series_longShort.csv", index=True, header=True)
    stats_longShort = summarize_performance(excess_returns_longShort, rf_monthly, spi_XsReturns_monthly, 12)
    save_summary_to_latex(stats_longShort, summary_file_path_longShort)
    # -----
    
    
    # Custom labels
    labels = {
        'Strategy_Returns': 'Long Momentum Strategy',
        'Benchmark': 'SPI',
        'Portfolio_Returns': 'Long Momentum Strategy',
        'xs_Return': 'Long Momentum Strategy',
        'trx_cost_0.001': 'Strategy with Trx Cost: 0.1%',
        'trx_cost_0.005': 'Strategy with Trx Cost: 0.5%',
        'trx_cost_0.01': 'Strategy with Trx Cost: 1.0%',
    }
    
    # Create plot and save it
    combined_returns = pd.concat([portfolio_returns_longOnly, portfolio_returns_longShort], axis=1)
    plot_cumulative_returns(combined_returns, spi_returns_monthly, labels,filename=visualization_path / "cumulative_returns")

    
    print("Performance summary saved successfully!")
    
    # Robustness checks
    
    # Over Holding Period
    # Loop over 1-12
    rc_holding_period = pd.DataFrame(index=range(1, 13), columns=['Sharpe_Ratio'])
    for i in range(1,13):
        excess_returnsTemp , _ , _, _ = momentum_strategy(
            price_data_daily=price_data_daily,
            lookback_period=lookback_period,
            nLong=nLong,
            nShort=0,
            holding_period=i,
            rf_monthly=rf_monthly,
            trx_cost=0
            )
        excess_returnsTemp.columns = ['Strategy_Returns']
        stats_temp = summarize_performance(excess_returnsTemp, rf_monthly, spi_XsReturns_monthly, 12)
        rc_holding_period.loc[i,'Sharpe_Ratio'] = stats_temp['Sharpe_Ratio_Arithmetic']['xs_Return']
        
    print("RC of Holding Period")
    print(rc_holding_period)
    
    plotRobustnessChecks(
        rc_holding_period,
        label = "Momentum Strategy",
        title='Sharpe Ratios over Holding Periods',
        x_label='Holding Period',
        y_label='Sharpe Ratio',
        savefig=True,
        filename=visualization_path / 'rc_holding_period.png'
    )

    
    # Over Lookback Period
    # Loop over 1-12
    rc_lookback_period = pd.DataFrame(index=range(1, 13), columns=['Sharpe_Ratio'])
    for i in range(1,13):
        excess_returnsTemp , _ , _, _ = momentum_strategy(
            price_data_daily=price_data_daily,
            lookback_period=i,
            nLong=nLong,
            nShort=0,
            holding_period=holding_period,
            rf_monthly=rf_monthly,
            trx_cost=0
            )
        excess_returnsTemp.columns = ['Strategy_Returns']
        stats_temp = summarize_performance(excess_returnsTemp, rf_monthly, spi_XsReturns_monthly, 12)
        rc_lookback_period.loc[i,'Sharpe_Ratio'] = stats_temp['Sharpe_Ratio_Arithmetic']['xs_Return']
        
    print("RC of Lookback Period")
    print(rc_lookback_period)
    
    plotRobustnessChecks(
        rc_lookback_period,
        label = "Momentum Strategy",
        title='Sharpe Ratios over Lookback Periods',
        x_label='Lookback Period',
        y_label='Sharpe Ratio',
        savefig=True,
        filename= visualization_path / 'rc_lookback_period.png'
    )
    
    
    # Over Number Assets
    # Loop over 5-50
    rc_number_assets = pd.DataFrame(index=range(5, 51), columns=['Sharpe_Ratio'])
    for i in range(5,51):
        excess_returnsTemp , _ , _, _ = momentum_strategy(
            price_data_daily=price_data_daily,
            lookback_period=lookback_period,
            nLong=i,
            nShort=0,
            holding_period=holding_period,
            rf_monthly=rf_monthly,
            trx_cost=0
            )
        excess_returnsTemp.columns = ['Strategy_Returns']
        stats_temp = summarize_performance(excess_returnsTemp, rf_monthly, spi_XsReturns_monthly, 12)
        rc_number_assets.loc[i,'Sharpe_Ratio'] = stats_temp['Sharpe_Ratio_Arithmetic']['xs_Return']
        
    print("RC of Number Assets")
    print(rc_number_assets)
    
    plotRobustnessChecks(
        rc_number_assets,
        label = "Momentum Strategy",
        title='Sharpe Ratios over Number Assets Long/Short',
        x_label='Number Assets Long/Short',
        y_label='Sharpe Ratio',
        savefig=True,
        filename=visualization_path / 'rc_number_assets.png'
    )
    
   
    
    # Over TRX cost
    # Initialize the DataFrame to hold the results
    rc_trxCost_XsRet = excess_returns_longOnly.copy()
    
    # List of transaction costs
    trxCosts = [0.001, 0.005, 0.01]
    
    # Loop through transaction costs and add the new columns
    for trx_cost in trxCosts:
        # Run the momentum strategy, here we need total ret not xs ret, for plot
        _, _, _, portfolio_returnsTemp = momentum_strategy(
            price_data_daily=price_data_daily,
            lookback_period=lookback_period,
            nLong=20,
            nShort=0,
            holding_period=holding_period,
            rf_monthly=rf_monthly,
            trx_cost=trx_cost
        )
        if isinstance(portfolio_returnsTemp, pd.Series):
            portfolio_returnsTemp = portfolio_returnsTemp.to_frame()
        portfolio_returnsTemp.columns = ['Strategy_Returns']

        # Generate the column name dynamically
        column_name = f"trx_cost_{trx_cost}"
        print(portfolio_returnsTemp.head)
        print(portfolio_returnsTemp.shape)
        print(type(portfolio_returnsTemp))
        # Add the new column to the DataFrame
        rc_trxCost_XsRet[column_name] = portfolio_returnsTemp['Strategy_Returns']
    # plot here
    plot_cumulative_returns(rc_trxCost_XsRet, spi_returns_monthly, labels,title='Robustness Check Transaction Costs', x_label='Date', y_label='Cumulative Returns', figsize=(12,6), grid=True, savefig=True, filename=visualization_path / 'rc_trxCost.png')

    print("Results saved successfully!")

if __name__ == '__main__':
    main()

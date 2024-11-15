# summarize_performance.py

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import skew, kurtosis

def summarize_performance(xs_returns, rf, factor_xs_returns, annualization_factor):
    """
    Computes annualized performance statistics including Sharpe ratio, alpha, beta, skewness, and kurtosis.

    Parameters:
    - xs_returns (pd.Series): Excess returns of the strategy.
    - rf (pd.Series): Risk-free rate for each period.
    - factor_xs_returns (pd.DataFrame): Factor excess returns for calculating alpha and beta.
    - annualization_factor (int): Annualization factor (e.g., 12 for monthly data).

    Returns:
    - results: Dictionary with performance metrics.
    """
    # Align the indices
    xs_returns = xs_returns.loc[rf.index].dropna()
    factor_xs_returns = factor_xs_returns.loc[rf.index].dropna()
    rf = rf.loc[xs_returns.index]

    # Total returns
    total_returns = xs_returns + rf

    # Compute geometric mean returns
    n_periods = len(xs_returns)
    final_rf = (1 + rf).prod()
    final_total_ret = (1 + total_returns).prod()
    geom_avg_rf = 100 * (final_rf ** (annualization_factor / n_periods) - 1)
    geom_avg_total_return = 100 * (final_total_ret ** (annualization_factor / n_periods) - 1)
    geom_avg_xs_return = geom_avg_total_return - geom_avg_rf

    # Standard deviation and mean excess returns
    std_xs_returns = xs_returns.std()
    xs_return_mean = xs_returns.mean()
    t_stats_xs_return = xs_return_mean / (std_xs_returns / np.sqrt(n_periods))

    # Regression for alpha and beta
    X = sm.add_constant(factor_xs_returns)
    model = sm.OLS(xs_returns, X).fit()
    alpha_arithmetic = model.params['const']
    betas = model.params.drop('const')
    t_stat_alpha = model.tvalues['const']

    # Geometric alpha based on benchmark
    bm_ret = factor_xs_returns.mul(betas).sum(axis=1) + rf
    final_bm_ret = (1 + bm_ret).prod()
    geom_avg_bm_return = 100 * (final_bm_ret ** (annualization_factor / n_periods) - 1)
    alpha_geometric = geom_avg_total_return - geom_avg_bm_return

    # Annualized statistics
    xs_returns_pct = 100 * xs_returns
    total_returns_pct = 100 * total_returns
    arithm_avg_total_return = annualization_factor * total_returns_pct.mean()
    arithm_avg_xs_return = annualization_factor * xs_returns_pct.mean()
    std_xs_returns_annualized = std_xs_returns * np.sqrt(annualization_factor)
    sharpe_arithmetic = arithm_avg_xs_return / std_xs_returns_annualized
    sharpe_geometric = geom_avg_xs_return / std_xs_returns_annualized

    # Additional descriptive statistics
    min_xs_return = xs_returns.min()
    max_xs_return = xs_returns.max()
    skew_xs_return = skew(xs_returns, nan_policy='omit')
    kurt_xs_return = kurtosis(xs_returns, nan_policy='omit')

    # Autocorrelations
    autocorrelations = {
        'Lag 1': xs_returns.autocorr(lag=1),
        'Lag 2': xs_returns.autocorr(lag=2),
        'Lag 3': xs_returns.autocorr(lag=3),
    }

    # Organize results into a dictionary
    results = {
        'Arithmetic_Avg_Total_Return': arithm_avg_total_return,
        'Arithmetic_Avg_Excess_Return': arithm_avg_xs_return,
        'Geometric_Avg_Total_Return': geom_avg_total_return,
        'Geometric_Avg_Excess_Return': geom_avg_xs_return,
        'Std_of_Excess_Returns_Annualized': std_xs_returns_annualized,
        'Sharpe_Ratio_Arithmetic': sharpe_arithmetic,
        'Sharpe_Ratio_Geometric': sharpe_geometric,
        'Min_Excess_Return': min_xs_return,
        'Max_Excess_Return': max_xs_return,
        'Skewness_of_Excess_Return': skew_xs_return,
        'Kurtosis_of_Excess_Return': kurt_xs_return,
        'Alpha_Arithmetic': annualization_factor * 100 * alpha_arithmetic,
        'Alpha_Geometric': alpha_geometric,
        'T_stat_of_Alpha': t_stat_alpha,
        'Beta': betas.to_dict(),
        'Std_Dev_of_Excess_Returns': std_xs_returns,
        'Monthly_Excess_Return': xs_return_mean,
        'T_stat_of_Monthly_Excess_Return': t_stats_xs_return,
        'Autocorrelations': autocorrelations,
    }

    return results

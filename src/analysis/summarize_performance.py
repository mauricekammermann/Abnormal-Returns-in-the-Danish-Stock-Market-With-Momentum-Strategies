import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis, t

def summarize_performance(xs_returns, rf, factor_xs_returns, annualization_factor):
    """
    Computes annualized performance statistics including Sharpe ratio, alpha, beta, skewness, and kurtosis.

    Parameters:
    - xs_returns (pd.DataFrame): Excess returns of the strategy, can be DataFrame with multiple assets.
    - rf (pd.Series or pd.DataFrame): Risk-free rate for each period.
    - factor_xs_returns (pd.DataFrame): Factor excess returns for calculating alpha and beta.
    - annualization_factor (int): Annualization factor (e.g., 12 for monthly data).

    Returns:
    - results: Dictionary with performance metrics.
    """

    # Ensure xs_returns and rf are DataFrames
    if isinstance(xs_returns, pd.Series):
        xs_returns = xs_returns.to_frame()
    if isinstance(rf, pd.Series):
        rf = rf.to_frame('rf')

    # Adjust the indices of xs_returns to align with rf and factor_xs_returns
    # Shift xs_returns index forward by one month
    xs_returns = xs_returns.copy()
    xs_returns.index = xs_returns.index + pd.DateOffset(months=1)

    # Align frequencies to month-end
    xs_returns = xs_returns.asfreq('M')
    rf = rf.asfreq('M')
    factor_xs_returns = factor_xs_returns.asfreq('M')

    # Align the indices
    common_index = xs_returns.index.intersection(rf.index).intersection(factor_xs_returns.index)
    xs_returns = xs_returns.loc[common_index]
    rf = rf.loc[common_index]
    factor_xs_returns = factor_xs_returns.loc[common_index]

    # Drop rows with any NaNs across all data
    data_combined = pd.concat([xs_returns, rf, factor_xs_returns], axis=1).dropna()
    xs_returns = data_combined[xs_returns.columns]
    rf = data_combined[rf.columns]
    factor_xs_returns = data_combined[factor_xs_returns.columns]

    # Ensure rf has same columns as xs_returns or is a single column
    if rf.shape[1] == 1:
        rf = pd.concat([rf]*xs_returns.shape[1], axis=1)
        rf.columns = xs_returns.columns
    elif rf.shape[1] != xs_returns.shape[1]:
        raise ValueError('rf must have either 1 column or the same number of columns as xs_returns')

    # Check if there is data after alignment
    n_periods = len(xs_returns)
    if n_periods == 0:
        raise ValueError("No data available after alignment and NaN removal. Please check your input data.")

    # Total returns
    total_returns = xs_returns + rf

    # Compute geometric mean returns
    final_rf = (1 + rf).prod()
    final_total_ret = (1 + total_returns).prod()
    geom_avg_rf = 100 * (final_rf ** (annualization_factor / n_periods) - 1)
    geom_avg_total_return = 100 * (final_total_ret ** (annualization_factor / n_periods) - 1)
    geom_avg_xs_return = geom_avg_total_return - geom_avg_rf

    # Standard deviation and mean excess returns
    std_xs_returns = xs_returns.std()
    xs_return_mean = xs_returns.mean()
    t_stats_xs_return = xs_return_mean / (std_xs_returns / np.sqrt(n_periods))

    # Regression for alpha and beta without statsmodels
    alpha_arithmetic = {}
    betas = {}
    t_stat_alpha = {}

    for col in xs_returns.columns:
        y = xs_returns[col]

        # Combine y and factors, drop NaNs
        data = pd.concat([y, factor_xs_returns], axis=1).dropna()
        y = data[col].values
        X = np.column_stack((np.ones(len(data)), data[factor_xs_returns.columns].values))

        # Check if there's enough data
        if len(y) < X.shape[1]:
            raise ValueError(f"Not enough data points to estimate parameters for {col}")

        # Calculate beta coefficients
        beta_hat = np.linalg.lstsq(X, y, rcond=None)[0]
        betas[col] = dict(zip(factor_xs_returns.columns, beta_hat[1:]))

        # Calculate residuals and estimated variance
        y_hat = X @ beta_hat
        residuals = y - y_hat
        sse = np.sum(residuals ** 2)
        degrees_of_freedom = len(y) - X.shape[1]
        sigma_squared = sse / degrees_of_freedom

        # Variance-Covariance Matrix
        cov_beta = sigma_squared * np.linalg.inv(X.T @ X)
        standard_errors = np.sqrt(np.diag(cov_beta))

        # t-statistics
        t_stats = beta_hat / standard_errors

        # Store alpha and its t-statistic
        alpha_arithmetic[col] = beta_hat[0]
        t_stat_alpha[col] = t_stats[0]

    # Convert betas to DataFrame
    betas_df = pd.DataFrame(betas).T  # Transpose to get assets as index

    # Geometric alpha based on benchmark
    bm_ret = factor_xs_returns.dot(betas_df.T) + rf
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
    skew_xs_return = xs_returns.apply(lambda x: skew(x, nan_policy='omit'))
    kurt_xs_return = xs_returns.apply(lambda x: kurtosis(x, nan_policy='omit'))

    # Autocorrelations
    autocorrelations = {}
    for col in xs_returns.columns:
        autocorrelations[col] = {
            'Lag 1': xs_returns[col].autocorr(lag=1),
            'Lag 2': xs_returns[col].autocorr(lag=2),
            'Lag 3': xs_returns[col].autocorr(lag=3),
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
        'Alpha_Arithmetic': pd.Series(alpha_arithmetic) * annualization_factor * 100,
        'Alpha_Geometric': alpha_geometric,
        'T_stat_of_Alpha': pd.Series(t_stat_alpha),
        'Beta': betas_df,
        'Std_Dev_of_Excess_Returns': std_xs_returns,
        'Monthly_Excess_Return': xs_return_mean,
        'T_stat_of_Monthly_Excess_Return': t_stats_xs_return,
        'Autocorrelations': autocorrelations,
    }

    return results

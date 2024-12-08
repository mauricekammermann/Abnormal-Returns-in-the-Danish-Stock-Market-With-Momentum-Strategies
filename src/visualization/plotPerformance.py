import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_cumulative_returns(df, benchmark=None, labels=None, title='Cumulative Returns Over Time', x_label='Date', y_label='Cumulative Returns (%)', figsize=(12,6), grid=True, savefig=True, filename='cumulative_returns.png'):
    """
    Plots cumulative returns over time for each asset in the dataframe or series.

    Parameters:
        df (pd.DataFrame or pd.Series): DataFrame or Series with dates as index and assets as columns (for DataFrame).
        benchmark (pd.DataFrame or pd.Series): Benchmark returns series or DataFrame with the same index as df.
        labels (dict): A dictionary mapping the columns or series names to custom labels for the legend.
        title (str): Title of the plot.
        x_label (str): Label for x-axis.
        y_label (str): Label for y-axis.
        figsize (tuple): Figure size.
        grid (bool): Whether to show grid lines.
        savefig (bool): Whether to save the figure.
        filename (str): Filename to save the figure.
    """
    # If df is a Series, convert it to a DataFrame
    if isinstance(df, pd.Series):
        if df.name is None:
            df = df.to_frame(name='Returns')
        else:
            df = df.to_frame()

    # Set plot style
    sns.set(style='whitegrid', context='talk')
    
    # Handle missing data
    df = df.fillna(0)
    
    # Compute cumulative returns for the main DataFrame
    cum_returns = (1 + df).cumprod()

    # If the benchmark is provided and is a DataFrame, handle it similarly to df
    if benchmark is not None:
        if isinstance(benchmark, pd.Series):
            benchmark = benchmark.to_frame(name='Benchmark') if benchmark.name is None else benchmark.to_frame()

        # Handle missing data in the benchmark
        benchmark = benchmark.fillna(0)

        # Compute cumulative returns for the benchmark
        benchmark_cum_returns = (1 + benchmark).cumprod()

        # Add benchmark cumulative returns to the cumulative returns DataFrame for consistency
        for column in benchmark_cum_returns.columns:
            cum_returns[column] = benchmark_cum_returns[column]

    # Use seaborn color palette
    palette = sns.color_palette('colorblind', n_colors=len(cum_returns.columns))
    
    # Create figure and axis objects
    fig, ax = plt.subplots(figsize=figsize)

    # Plot using Seaborn
    if benchmark is not None:
        for i, column in enumerate(cum_returns.columns):
            label = labels[column] if labels and column in labels else column
            color = palette[i] if column not in benchmark.columns else 'black'
            linewidth = 2
            sns.lineplot(data=cum_returns[column], ax=ax, label=label, color=color, linewidth=linewidth)
    else:
        for i, column in enumerate(cum_returns.columns):
            label = labels[column] if labels and column in labels else column
            color = palette[i]
            linewidth = 2
            sns.lineplot(data=cum_returns[column], ax=ax, label=label, color=color, linewidth=linewidth)
       
    
    # Set title and labels
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend()
    
    if grid:
        ax.grid(True)
    else:
        ax.grid(False)

    # Rotate date labels if necessary
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    if savefig:
        print(f"Save the summarize performance plot to {filename}")
        plt.savefig(filename, dpi=300)
    
    plt.show()

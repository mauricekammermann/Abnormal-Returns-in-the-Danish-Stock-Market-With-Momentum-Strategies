


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_cumulative_returns(df, title='Cumulative Returns Over Time', x_label='Date', y_label='Cumulative Returns', figsize=(12,6), grid=True, savefig=True, filename='//wsl.localhost/Ubuntu/home/maurice/Visuals/cumulative_returns.png'):
    """
    Plots cumulative returns over time for each asset in the dataframe or series.

    Parameters:
        df (pd.DataFrame or pd.Series): DataFrame or Series with dates as index and assets as columns (for DataFrame).
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
    
    # Compute cumulative returns
    cum_returns = (1 + df).cumprod()
    
    # Use seaborn color palette
    palette = sns.color_palette('husl', n_colors=len(cum_returns.columns))
    
    # Plot
    plt.figure(figsize=figsize)
    for i, column in enumerate(cum_returns.columns):
        plt.plot(cum_returns.index, cum_returns[column], label=column, color=palette[i])
    
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    if grid:
        plt.grid(True)
    else:
        plt.grid(False)
    
    # Rotate date labels if necessary
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    if savefig:
        print(f"Save the summarize performance plot to {filename}")
        plt.savefig(filename, dpi=300)
    
    plt.show()

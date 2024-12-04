import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plotRobustnessChecks(df, label='Series', title='Robustness Check', x_label='Variable', y_label='Value', figsize=(12,6), grid=True, savefig=False, filename='robustness_check.png', linewidth=3):
    """
    Plots robustness checks over a variable (e.g., holding period) for each asset or strategy.

    Parameters:
        df (pd.DataFrame or pd.Series): DataFrame or Series where the index is a variable (e.g., holding period) and columns are corresponding values (e.g., Sharpe ratios).
        label (str): Label for the series in the legend.
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
            df = df.to_frame(name='Value')
        else:
            df = df.to_frame()
    
    # Set plot style
    sns.set(style='whitegrid', context='talk')
    
    # Handle missing data
    df = df.dropna()
    
    # Use seaborn color palette
    palette = sns.color_palette('colorblind', n_colors=len(df.columns))
    
    # Plot
    plt.figure(figsize=figsize)
    for i, column in enumerate(df.columns):
        plt.plot(df.index, df[column], label=label if len(df.columns) == 1 else column, color=palette[i], linewidth=linewidth)
    
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    
    if grid:
        plt.grid(True)
    else:
        plt.grid(False)
    
    # Rotate x-axis labels if they are not numeric
    if not pd.api.types.is_numeric_dtype(df.index):
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    if savefig:
        plt.savefig(filename, dpi=300)
        #print(f"Plot saved as {filename}")
    
    plt.show()

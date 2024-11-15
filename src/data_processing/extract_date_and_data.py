#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 12:27:37 2024

@author: steve
"""
import pandas as pd

def extract_date_and_data(df):
    """
    Processes a DataFrame to extract and format the date column, and return the rest of the data.
    
    Parameters:
    - df (pd.DataFrame): DataFrame with a "date" column in the format "yyyy-mm-dd" as the first column.

    Returns:
    - formatted_date (pd.Series): Series with dates formatted as "yyyymmdd" (int).
    - data (pd.DataFrame): DataFrame with the remaining columns.
    """
    # Convert the "date" column to datetime format
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    
    # Format the date column as "yyyymmdd" integer
    formatted_date = df['date'].dt.strftime('%Y%m%d').astype(int)
    
    # Drop the "date" column to get the rest of the data
    data = df.drop(columns=['date'])
    
    return formatted_date, data
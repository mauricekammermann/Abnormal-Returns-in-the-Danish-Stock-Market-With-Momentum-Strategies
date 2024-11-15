#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 20:37:21 2024

@author: steve
"""
import sys
import logging
import pandas as pd
import numpy as np
from src.data_processing import data_processing
import backtest_functions


def main():
    pass


# Ensures the script runs only when executed directly (not when imported)
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)
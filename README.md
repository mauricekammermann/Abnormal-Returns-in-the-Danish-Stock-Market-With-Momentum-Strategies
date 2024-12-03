# Swiss Performance Index (SPI) Momentum Strategy

In this project, we investigate whether the momentum effect, first documented by Jegadeesh and Titman (1993), persists in Switzerland to this day and to what extent it can generate abnormal net returns.

The momentum effect describes the tendency of assets that have performed well in the recent past to continue outperforming in the near future, and vice versa for poor performers, contradicting the weak form of the efficient market hypothesis. However, the biggest drawback of momentum strategies is transaction costs, which diminish returns due to frequent portfolio turnover. Our primary aim, therefore, is to replicate and extend the work of Jegadeesh and Titman (1993) within the Swiss stock market context, while addressing these practical implementation challenges.

We proxy the Swiss stock market using the constituents of the Swiss Performance Index (SPI) and test the effectiveness of classical momentum strategies from 2000 to 2024. We examine the robustness of these strategies by varying lookback periods, holding periods, and transaction costs. Our results (add results)

Reference for results the juptyer notebook, report and presentation.

Add Final main picture of our results.

## Project Organization
------------

    ├── README.md                    <- The top-level README for developers using this project, including requirements and updating solutions.
    ├── Dockerfile                   <- Dockerfile to recreate the entire project in Docker.
    ├── SPI_momentum.yaml            <- .yaml file with requirements to create environment in Docker.
    ├── data
    │   ├── processed                <- Final data sets that can be used for modeling.
    │   ├── interim                  <- Intermediate data that has been transformed.
    │   ├── raw                      <- The original data dump.
    │   └── results                  <- Results from our analysis.
    │
    ├── notebook                     <- Juptyer Notebook for interactive results.
    ├── reports                      <- Generated analysis as PDF, LaTeX, etc.
    │   ├── report                   <- Final report as PDF and LaTex.
    │   ├── presentation             <- Final presentation as PDF and LaTex.
    │   └── figures                  <- Generated graphics, plots and figures used in reporting.
    │
    ├── src                          <- Source code for use in this project.
    │   ├── analysis                 <- Source code used for analysis.
    │   ├── data_processing          <- Source code used to fetch, load and process data.
    │   └── visualization            <- Source code used to generate visualizations.
    
--------

## Data and Data Processing
In this research project, we utilized data from Datastream and the Swiss National Bank (SNB) spanning the period from 2000 to 2024. Data from Datastream (total return of the constituents in the SPI and SPI itself) and data from the SNB (monthly yield of 1 year Swiss Federal Bonds) are provided. Note that data is only used for academic research and not to be commercialized.

The [provided data processors](src/data_processing) clean the .xlsx and .csv by removing headers and unnecessary information. Then, they save the processed files as a .csv file with the correct name in [data/processed](data/processed). 

Updating the data could work as follows, assuming you have access to a Datastream-Refinitiv portal:
1. Download and open the Excel file [SPI_Data_Datastream](data/raw/SPI_Data_Datastream.xlsx) and pull the newest data.
2. Fetch the newest SNB data with the [data_fetcher_snb.py](datafeed/data_fetcher_snb.py), adjusting the API link with the desired dates. It should be saved automatically in [data/raw](data/raw) as `snb_yield_data.csv`.
3. Then, please run the [data processor](src/data_processing/main.py). The processed .csv files should be automatically saved in [data/processed](data/processed) with the correct name.

If desired to use own data, please place the desired .xlsx files in [data/raw](data/raw), named and structured identically to the current files, and run the data processors in [src/data_processing](src/data_processing). If you wish to analyze a different market than the Swiss market, please replace the data in [data/raw](data/raw) with data from your chosen country, maintaining the original file structure. The data processor should still work, but please adjust the input and output file names in the data processor scripts in [src/data_processing](src/data_processing) to match your new data files and desired output names. Furthermore, update the file names in the source code located in [analysis](src/analysis) to reference the newly processed data files. 

## Reproducibility of Project
This entire project aims to be fully reproducible. In order to do this, we provide two methods of replicating our project: (1) GitHub Repo Cloning and (2) Docker Containerization.  
### (1) GitHub Repo Cloning
Describe how to clone repo and how to run jupyter notebook and how to compile LaTeX.

### (2) Docker
This entire project has been Dockerized for easier deployment and ensuring full reproducibility. Follow these steps if you want to use docker:

SHOW HOW TO COMPILE LATEX AS WELL!
1. Install Docker
```bash
    Installation guide
```
2. Build Docker container with Docker image
```bash
    Installation guide
```
3. Run the Docker container
```bash
    Installation guide
```
4. Activate the virtual environemnt
```bash
    Installation guide
```
5. Optional: Converting the Jupyter Notebook to a .py file, if desired
```bash
    Installation guide
```
6. Start the Jupyter notebook server in the background
```bash
    Installation guide
```
7. Optional: Running the Python file intead of Jupyter notebook:
```bash
    Installation guide
```

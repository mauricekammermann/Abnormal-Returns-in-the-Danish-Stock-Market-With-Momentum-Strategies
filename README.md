# Swiss Performance Index (SPI) Momentum Strategy
In this project, we investigate to what extent a momentum strategy (such as the one proposed by Jegadeesh and Titman (1993)) generates significant abnormal returns in the Swiss stock market after transaction costs. 

Add some literature review, data, and results.

Reference for results the juptyer notebook, report and presentation.

Add Final main picture of our results.

## Project Organization
------------

    ├── README.md                    <- The top-level README for developers using this project, including requirements and updating solutions.
    ├── Dockerfile                   <- Dockerfile to recreate the entire project in Docker.
    ├── SPI_momentum.yaml            <- .yaml file with requirements to create environment in Docker.
    ├── data
    │   ├── data_fetcher_snb.py      <- Script to download risk-free rates from SNB, using their API.
    │   ├── processed                <- Final data sets that can be used for modeling.
    │   ├── interim                  <- Intermediate data that has been transformed.
    │   └── raw                      <- The original data dump.
    │
    ├── notebook                     <- Juptyer Notebook for interactive results.
    ├── reports                      <- Generated analysis as PDF, LaTeX, etc.
    │   ├── report                   <- Final report as PDF and LaTex.
    │   ├── presentation             <- Final presentation as PDF and LaTex.
    │   └── figures                  <- Generated graphics, plots and figures used in reporting.
    │
    ├── src                          <- Source code for use in this project.
    │   ├── analysis                 <- Source code used for analysis.
    │   ├── data_processing          <- Source code used to load and process data.
    │   └── visualization            <- Source code used to generate visualizations.
    
--------

## Data

Data from Refinitiv (total return of the constituents in the SPI and SPI itself, close prices of the constituents in the SPI and SPI itself) and data from the Swiss National Bank (SNB) (monthly yield of 3 month Swiss Federal Bonds) are provided. Note that data is only used for academic research and not to be commercialized.

The data processors do this and this.

Updating the data could work as follows, assuming you have access to a Datastream-Refinitiv portal:
1. Download and open the [Excel file](data/raw/SPI_Data_Datastream_raw.xlsx) and pull the newest data.
2. Then, run the [Refinitiv data processor](data_processing/refinitiv_data_processing.py) and save it as `refinitiv_data.csv` in [data/processed](data/processed).
3. Fetch the newest SNB-data with the [data_fetcher.py](datafeed/data_fetcher_snb.py), adjusting the API link with the desired dates. It should be saved automatically in [data/raw](data/raw) as `snb_yield_data.csv`.
4. Then, run the [SNB data processor](data_processing/snb_data_processing.py) and save it as `risk_free.csv` in [data/processed](data/processed).

If desired to use own data, please place the desired .xlsx files in [data/raw](data/raw), named and structured identically to the current files, and run the data processors in [src/data_processing](src/data_processing). If you wish to analyze a different market than the Swiss market, please replace the data in [data/raw](data/raw) with data from your chosen country, maintaining the original file structure. The data processors should still work, but please adjust the input and output file names in the data processor scripts in [src/data_processing](src/data_processing) to match your new data files and desired output names. Furthermore, update the file names in the source code located in [analysis](src/analysis) to reference the newly processed data files. 

## Requirements
Describe how to clone repo and how to run jupyter notebook

## Docker
This entire project has been Dockerized for easier deployment and ensuring full reproducibility. Follow these steps if you want to use docker:

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
5. Activate the virtual environemnt
```bash
    Installation guide
```
7. Optional: Converting the Jupyter Notebook to a .py file, if desired
```bash
    Installation guide
```
9. Start the Jupyter notebook server in the background
```bash
    Installation guide
```
11. Optional: Running the Python file intead of Jupyter notebook:
```bash
    Installation guide
```

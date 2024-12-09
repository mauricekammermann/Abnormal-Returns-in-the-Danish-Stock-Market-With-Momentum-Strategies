# Swiss Performance Index (SPI) Momentum Strategy

In this project, we investigate whether the long only momentum effect, first documented by Jegadeesh and Titman (1993), persists in Switzerland to this day and to what extent it can generate abnormal net returns.

The momentum effect describes the tendency of assets that have performed well in the recent past to continue outperforming in the near future, and vice versa for poor performers, contradicting the weak form of the efficient market hypothesis. While momentum strategies have shown promise in generating above-average returns, their biggest drawback is the high transaction costs associated with frequent portfolio turnover. These costs can significantly diminish the strategy's profitability, making practical implementation challenging for investors. Given these circumstances, we are particularly interested in examining whether long-only momentum strategies can still generate abnormal returns in the Swiss market after transaction costs. Our primary aim is, therefore, to replicate the work of Jegadeesh and Titman (1993) within the context of the Swiss stock market, while addressing these practical implementation challenges.

This study examines the effectiveness of long-only momentum strategies in the Swiss stock market from 2000 to 2024, using constituents of the Swiss Performance Index (SPI) as a proxy. The robustness of these strategies is tested by varying lookback periods, holding periods, and transaction costs. Our results indicate that long-only momentum strategies in the Swiss market can indeed generate significant abnormal net returns, even after accounting for transaction costs, and outperform the SPI benchmark. However, consistent with previous research, the profitability of these strategies decreases notably with higher transaction costs due to portfolio turnover. Despite that, in terms of overall performance, long/short momentum strategies appear to outperform their long-only counterparts.

We invite you to take a look at our [report](reports/report/SPI-Momentum_Report.pdf) and [beamer presentation](reports/presentation/SPI-Momentum_Presentation.pdf) with fully reproducible LaTeX source code. You can use Overleaf or Docker (see below) to compile the PDF yourself. Please also take a look at our [Jupyter Notebook](notebook/SPI_Momentum.ipynb) for interactive results, either on GitHub, Docker or on your local machine (see below as well, "Reproducibility of Project"). 

![rc_trxCost (1)](https://github.com/user-attachments/assets/9e2ab42f-0079-429f-9f8a-aa20721ff05c)

## Project Organization
------------

    ├── README.md                    <- The top-level README for developers using this project, including requirements and updating solutions.
    ├── Dockerfile                   <- Dockerfile to recreate the entire project in Docker.
    ├── requirements.txt             <- .txt file with requirements to create environment in Docker.
    ├── data
    │   ├── processed                <- Final data sets that can be used for modeling.
    │   ├── interim                  <- Intermediate data that has been transformed.
    │   ├── raw                      <- The original data dump.
    │   └── results                  <- Results from our analysis.
    │
    ├── notebook                     <- Juptyer Notebook for interactive results.
    ├── reports                      <- Generated analysis as PDF, LaTeX, etc.
    │   ├── report                   <- Final report as PDF and LaTeX.
    │   ├── presentation             <- Final presentation as PDF and LaTex.
    │   └── figures                  <- Generated graphics, plots and figures used in reporting.
    │
    ├── src                          <- Source code for use in this project.
    │   ├── analysis                 <- Source code used for analysis.
    │   ├── data_processing          <- Source code used to fetch, load and process data.
    │   └── visualization            <- Source code used to generate visualizations.
    
--------

## Data and Data Processing
In this research project, we utilized a dataset spanning from January 2000 to October 2024, sourced from Datastream and the Swiss National Bank (SNB). The dataset comprises total return data for the Swiss Performance Index (SPI) and its constituents from Datastream, as well as monthly yields of 1-year Swiss Federal Bonds from the SNB. Datastream data is split into two separate Excel files: One for the index itself ([SPI_Index_Data](data/raw/SPI_Index_Data.xlsx)) and one for the constituents ([SPI_Constituents_Data](data/raw/SPI_Constituents_Data.xlsx)). The SPI will serve as the benchmark for the long only strategy. Note that data is only used for academic research and not to be commercialized.

The [provided data processors](src/data_processing) clean the .xlsx and .csv by removing headers and unnecessary information. Then, they save the processed files as a .csv file with the correct name in [data/processed](data/processed). 

Updating the data could work as follows, assuming you have access to a Datastream-Refinitiv portal:
1. Download and open the Excel files ([SPI_Index_Data](data/raw/SPI_Index_Data.xlsx) & [SPI_Constituents_Data](data/raw/SPI_Constituents_Data.xlsx)) and and pull the newest data.
2. Adjust the API link in [data_fetcher_snb](src/data_processing/data_fetcher_snb.py) with the desired dates. 
3. Then, please run the data processor [main.py](src/data_processing/main.py). The processed .csv files should be automatically saved in [data/processed](data/processed) with the correct name.

If desired to use own data, please place the desired .xlsx files in [data/raw](data/raw), named and structured identically to the current files, and run the data processors in [src/data_processing](src/data_processing). If you wish to analyze a different market than the Swiss market, please replace the data in [data/raw](data/raw) with data from your chosen country, maintaining the original file structure. The data processor should still work, but please adjust the input and output file names in the data processor scripts in [src/data_processing](src/data_processing) to match your new data files and desired output names. Furthermore, update the file names in the source code located in [analysis](src/analysis) to reference the newly processed data files. 

## Reproducibility of Project: Docker
This entire project aims to be fully reproducible, thus it has been fully Dockerized for easier deployment. Follow these steps if you want to use docker. We recommend using [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).

1. Please clone our repo on your local machine in the desired location. 
```bash
git clone https://github.com/mauricekammermann/SPI-Momentum.git
```

2. If you do not have Git and Docker installed, please do so: [Git Installating Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker Installation Guide](https://docs.docker.com/engine/install/).

3. Change the directory to where you cloned the repo to before, and build Docker image.
```bash
cd SPI-Momentum #please adjust name accordingly
docker build -t spi-momentum .
```
4. Run the Docker container. The Jupyter server should start in the background. You can copy paste the URL in the terminal and run the [Jupyter Notebook](notebook/SPI_Momentum.ipynb).
```bash
docker run -it -p 8888:8888 spi-momentum #omit -it if not needed
```
5. Feel free to compile the .tex documents yourself with `pdflatex`
```bash
docker run -it -p 8818:8818 spi-momentum bash

#compiling report as pdf
cd reports/report/
pdflatex main_report.tex

#compiling beamer as pdf
cd reports/presentation/
pdflatex main_presentation.tex
```




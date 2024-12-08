# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies, including LaTeX packages and biber
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-xetex \
    texlive-bibtex-extra \
    texlive-science \
    biber \
    lmodern \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements.txt and install Python dependencies (if any)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Compile the LaTeX document
RUN cd /app/reports/report && \
    pdflatex main_report.tex && \
    biber main_report && \
    pdflatex main_report.tex && \
    pdflatex main_report.tex


# Expose port 8888 for Jupyter Notebook
EXPOSE 8888

# Default command to run Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root"]

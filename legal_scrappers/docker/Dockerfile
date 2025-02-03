# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy only requirements first (better for Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the code
COPY . .

# Command to run (this can be modified for different entry points)
CMD ["python", "scrapers/dcaf_scraper.py"]

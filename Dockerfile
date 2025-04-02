FROM python:3.12.9-slim-bookworm

WORKDIR /app

# Create a non-root user for running the application
RUN adduser --disabled-password --gecos '' keerthigowda

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ /app/src/
COPY gunicorn.conf.py /app/

# Create necessary directories
RUN mkdir -p /app/src/logs && \
    mkdir -p /app/src/geodb

# Set proper ownership
RUN chown -R keerthigowda:keerthigowda /app

# Switch to non-root user
USER keerthigowda

EXPOSE 8080

CMD ["gunicorn", "-c", "gunicorn.conf.py", "src.app:app"]


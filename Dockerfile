FROM python:3.11-slim

WORKDIR /app

# Create a non-root user for running the application
RUN adduser --disabled-password --gecos '' keerthigowda

# Copy only requirements first to leverage Docker caching
COPY requirements.txt /app/

# Install dependencies before copying app code
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Set proper ownership
RUN chown -R keerthigowda:keerthigowda /app

# Switch to non-root user
USER keerthigowda

EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "--timeout", "120", "--log-level", "info", "app:app"]


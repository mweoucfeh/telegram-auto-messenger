FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY pyproject.toml .
COPY README.md .

# Install the package
RUN pip install -e .

# Create directories for data and config
RUN mkdir -p /app/data /app/config /app/sessions /app/logs

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash telegram
RUN chown -R telegram:telegram /app
USER telegram

# Expose port (if needed for future web interface)
EXPOSE 8080

# Default command
CMD ["telegram-auto-messenger", "run"]
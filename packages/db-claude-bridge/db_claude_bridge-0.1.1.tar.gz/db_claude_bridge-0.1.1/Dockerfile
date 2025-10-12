FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Databricks CLI
RUN curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/

# Change ownership to app user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Install the package
RUN pip install -e .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD databricks-claude --version || exit 1

# Default command
CMD ["databricks-claude", "--help"]



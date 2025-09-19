# Stage 1: Get uv from official image
FROM ghcr.io/astral-sh/uv:0.8.14 AS uv-installer

# Stage 2: Final runtime image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy uv from the official uv image
COPY --from=uv-installer /uv /usr/local/bin/uv

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies as root (this keeps .venv owned by root for security)
RUN uv sync --frozen

# Copy source code 
COPY src/prepro ./src/prepro

# Create a non-root user and set up proper permissions
RUN useradd -m appuser && \
    mkdir -p /app/tmp_etl && \
    # Only give appuser ownership of tmp_etl (working directory)
    chown -R appuser:appuser /app/tmp_etl && \
    # Keep source code and .venv owned by root (read-only for security)
    chmod -R 755 /app/src && \
    chmod -R 755 /app/tmp_etl

# Switch to non-root user
USER appuser

# Also set PYTHONPATH to ensure the prepro module can be found
ENV PYTHONPATH=/app/src

# Use uv run with --no-sync to avoid trying to modify .venv at runtime
ENTRYPOINT ["uv", "run", "--no-sync", "python", "src/prepro/pipeline.py"]
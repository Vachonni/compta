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

# Install dependencies first (before copying source code)
RUN uv sync

# Copy source code after dependencies for better caching
COPY src/prepro ./src/prepro

# Create a non-root user
RUN useradd -m appuser \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (adjust if your app uses a different port)
# EXPOSE 8000

# Run (something like: CMD or ENTRYPOINT ["uv", "run", ..........])
ENTRYPOINT ["uv", "run", "python", "src/prepro/pipeline.py"]


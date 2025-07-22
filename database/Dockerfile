# Stage 1: Get uv from official image
FROM ghcr.io/astral-sh/uv:latest AS uv-installer

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
COPY src/database_pkg ./database_pkg

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Expose port (adjust if your app uses a different port)
EXPOSE 8000

# Run the app using uv and uvicorn (from README)
CMD ["uv", "run", "uvicorn", "database_pkg.app:app", "--host", "0.0.0.0", "--port", "8000"]

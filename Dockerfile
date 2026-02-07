# Build stage
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install uv

# Copy project files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system -e ".[dev]"

# Production stage
FROM python:3.13-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 jiri && \
    chown -R jiri:jiri /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=jiri:jiri . .

# Switch to non-root user
USER jiri

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

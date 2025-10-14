# Multi-stage Docker build for SensorThings API Validator
# Stage 1: Builder
FROM python:3.11-slim AS builder

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files and source code (needed for package build)
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.11-slim

# Set metadata
LABEL org.opencontainers.image.title="OGC STA Schema Validator"
LABEL org.opencontainers.image.description="Validation tool for OGC SensorThings API entities against configurable JSON schemas"
LABEL org.opencontainers.image.source="https://github.com/janbeckert/ogc-sta-schema-validator"
LABEL org.opencontainers.image.licenses="MIT"

# Create non-root user for security
RUN groupadd -r validator && useradd -r -g validator validator

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=validator:validator /app/.venv /app/.venv

# Copy application code
COPY --chown=validator:validator src/ ./src/
COPY --chown=validator:validator config/config.example.yaml ./config/
COPY --chown=validator:validator examples/ ./examples/

# Create directories for user-provided configs and schemas
RUN mkdir -p /app/config /app/schemas /app/output && \
    chown -R validator:validator /app/config /app/schemas /app/output

# Set PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Switch to non-root user
USER validator

# Set entrypoint to the CLI tool
ENTRYPOINT ["python", "-m", "src.cli"]

# Default command - show help
CMD ["--help"]

# Health check (optional - requires adding a health endpoint)
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#   CMD python validate.py test-connection || exit 1

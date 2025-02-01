# Stage 1: Build dependencies
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir build && \
    python -m build --wheel --no-isolation

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 bot && \
    chown -R bot:bot /app

# Copy built wheel from builder
COPY --from=builder /app/dist/*.whl .

# Install production dependencies
RUN pip install --no-cache-dir *.whl && \
    rm *.whl

# Copy application files
COPY config/ config/
COPY app/ app/
COPY main.py .

# Switch to non-root user
USER bot

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/bot/.local/bin:$PATH"

# Run the bot
CMD ["python", "main.py"] 
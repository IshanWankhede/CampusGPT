FROM python:3.11-slim

# Create dedicated non-root application user and group (UID/GID 10001)
RUN groupadd -g 10001 appgroup \
    && useradd -u 10001 -g appgroup -s /bin/sh -m appuser

WORKDIR /app

# Install runtime dependencies only (AI packages moved to requirements-ai.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and migration files
COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic

# Ensure app directory is owned by the non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root execution
USER appuser

EXPOSE 8000

# Dedicated entrypoint: API container never automatically executes migrations
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

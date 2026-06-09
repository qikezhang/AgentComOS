FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AGENTCOMOS_ENV=production

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy project files
COPY src/ src/
COPY docs/ docs/
COPY schemas/ schemas/
COPY scripts/ scripts/

CMD ["python3", "-m", "agentcomos.cli", "healthcheck"]

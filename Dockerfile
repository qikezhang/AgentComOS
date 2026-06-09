FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AGENTCOMOS_ENV=production

# Copy project files needed for installation
COPY pyproject.toml README.md ./
COPY src/ src/
COPY docs/ docs/
COPY schemas/ schemas/
COPY scripts/ scripts/

# Install dependencies and the project
RUN pip install --no-cache-dir .

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD agentcomos healthcheck || exit 1

CMD ["agentcomos", "healthcheck"]

# ─────────────────────────────────────────────────────────
# Fleet Telemetry Analyzer — Multi-stage Docker build
# ─────────────────────────────────────────────────────────

FROM python:3.12-slim AS base

LABEL maintainer="Fleet Telemetry Team"
LABEL description="Fleet telemetry analysis MCP server and CLI tool"

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ─── Dependencies ───
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Application code ───
COPY src/ src/
COPY data/ data/
COPY tests/ tests/

# ─── Default: run CLI analysis on sample data ───
# Override with docker-compose or docker run arguments
ENTRYPOINT ["python", "-m", "src.main"]
CMD ["data/sample_report.json"]

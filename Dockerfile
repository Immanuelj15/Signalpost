FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

# Copy application source
COPY src/ ./src/
COPY data/ ./data/
COPY docs/ ./docs/
COPY scripts/ ./scripts/
COPY .env.example .env

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Default command: show CLI help
CMD ["python", "-m", "signalpost.cli", "--help"]

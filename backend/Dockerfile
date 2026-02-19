FROM python:3.11-slim

WORKDIR /app

# Install system dependencies + Doppler CLI
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    && curl -sLf --retry 3 --tlsv1.2 --proto "=https" \
       'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' \
       | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] \
       https://packages.doppler.com/public/cli/deb/debian any-version main" \
       | tee /etc/apt/sources.list.d/doppler-cli.list \
    && apt-get update && apt-get install -y doppler \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./worker.py ./worker.py
COPY ./alembic.ini ./alembic.ini
COPY ./alembic ./alembic

# Expose port
EXPOSE 8000

# Default command runs the API server; override for worker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

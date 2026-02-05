# CAMARA FastMCP Server - Simple, compatible Dockerfile

FROM python:3.13-slim

WORKDIR /app

# Install system dependencies (optional but safe)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements_fastmcp.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_fastmcp.txt

# Copy application
COPY camara_final_complete.py /app/

# Non-root user (optional but recommended)
RUN useradd -m -u 1001 mcpuser && \
    chown -R mcpuser:mcpuser /app
USER mcpuser

ENV CAMARA_VERSION=spring25
ENV CAMARA_TIMEOUT=30

EXPOSE 8000

# Default: server mode for Docker/K8s
CMD ["python", "camara_final_complete.py", "--server", "--host", "0.0.0.0", "--port", "8000"]
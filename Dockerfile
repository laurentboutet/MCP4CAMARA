# CAMARA FastMCP Server - Production Dockerfile
FROM python:3.13-slim AS builder

WORKDIR /app
COPY requirements_fastmcp.txt .
RUN pip install --no-cache-dir --user -r requirements_fastmcp.txt

# Production image
FROM python:3.13-alpine

# Install runtime dependencies
RUN apk add --no-cache bash curl && \
    adduser -D mcpuser && \
    mkdir -p /app /config

WORKDIR /app

# Copy installed packages
COPY --from=builder /root/.local /home/mcpuser/.local

# Copy application
COPY camara_final_complete.py /app/
COPY .env.example /config/.env.example

# Security: non-root user
USER mcpuser
ENV PATH=/home/mcpuser/.local/bin:$PATH

# Default environment variables
ENV CAMARA_VERSION=spring25
ENV CAMARA_TIMEOUT=30

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose MCP server port
EXPOSE 8000

# Default: server mode for Docker/K8s
CMD ["python", "camara_final_complete.py", "--server", "--host", "0.0.0.0", "--port", "8000"]

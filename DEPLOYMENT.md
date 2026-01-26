# Deployment Guide

Complete deployment guide for CAMARA FastMCP Server in various environments.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Docker Compose](#docker-compose)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Production Best Practices](#production-best-practices)
5. [Monitoring & Logging](#monitoring--logging)

---

## Docker Deployment

### Quick Start

```bash
# 1. Build image
docker build -t camara-mcp:latest .

# 2. Run container
docker run -d \
  --name camara-mcp \
  -p 8000:8000 \
  -e CAMARA_BASE_URL=https://api.example-operator.com \
  -e CAMARA_API_KEY=your-token \
  -e CAMARA_VERSION=spring25 \
  camara-mcp:latest

# 3. Test
curl http://localhost:8000/health
```

### Build Options

**Production build:**
```bash
docker build -t camara-mcp:v1.0.0 \
  --build-arg PYTHON_VERSION=3.13 \
  --target production \
  .
```

**Development build:**
```bash
docker build -t camara-mcp:dev \
  --target builder \
  .
```

### Environment Variables

```bash
docker run -d \
  -e CAMARA_BASE_URL=https://operator.com \
  -e CAMARA_API_KEY=bearer-token \
  -e CAMARA_VERSION=spring25 \
  -e CAMARA_TIMEOUT=30 \
  -e MCP_LOG_LEVEL=debug \
  camara-mcp:latest
```

### Volume Mounts

```bash
# Mount logs directory
docker run -d \
  -v ./logs:/app/logs \
  -v ./config/.env:/config/.env:ro \
  camara-mcp:latest
```

### Health Checks

```bash
# Docker health check
docker inspect --format='{{.State.Health.Status}}' camara-mcp

# Manual health check
curl -f http://localhost:8000/health || echo "unhealthy"
```

---

## Docker Compose

### Basic Setup

```bash
# 1. Create .env file
cp .env.example .env
# Edit with your credentials

# 2. Start services
docker-compose up -d

# 3. View logs
docker-compose logs -f camara-mcp

# 4. Stop services
docker-compose down
```

### Production Setup with Nginx

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  camara-mcp-1:
    image: camara-mcp:latest
    environment:
      - CAMARA_BASE_URL=\${CAMARA_BASE_URL}
      - CAMARA_API_KEY=\${CAMARA_API_KEY}
    networks:
      - backend

  camara-mcp-2:
    image: camara-mcp:latest
    environment:
      - CAMARA_BASE_URL=\${CAMARA_BASE_URL}
      - CAMARA_API_KEY=\${CAMARA_API_KEY}
    networks:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - camara-mcp-1
      - camara-mcp-2
    networks:
      - backend

networks:
  backend:
    driver: bridge
```

### Scaling

```bash
# Scale to 5 instances
docker-compose up -d --scale camara-mcp=5

# Check running instances
docker-compose ps
```

---

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Verify cluster connection
kubectl cluster-info
kubectl get nodes
```

### Quick Deploy

```bash
# 1. Edit secrets
vim k8s/camara-secrets.yaml
# Add your CAMARA_BASE_URL and CAMARA_API_KEY

# 2. Apply manifests
kubectl apply -f k8s/camara-secrets.yaml
kubectl apply -f k8s/camara-deployment.yaml
kubectl apply -f k8s/camara-service.yaml

# 3. Verify deployment
kubectl get pods -l app=camara-mcp
kubectl get svc camara-mcp-service
kubectl get ingress camara-mcp-ingress

# 4. Check logs
kubectl logs -l app=camara-mcp --tail=50 -f
```

### Configuration

**Update secrets:**
```bash
kubectl create secret generic camara-secrets \
  --from-literal=base-url=https://operator.com \
  --from-literal=api-key=your-token \
  --dry-run=client -o yaml | kubectl apply -f -
```

**Update ConfigMap:**
```bash
kubectl create configmap camara-config \
  --from-literal=CAMARA_VERSION=fall25 \
  --from-literal=CAMARA_TIMEOUT=60 \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up changes
kubectl rollout restart deployment/camara-mcp
```

### Scaling

**Manual scaling:**
```bash
kubectl scale deployment camara-mcp --replicas=5
```

**Auto-scaling (HPA):**
```bash
# Already configured in k8s/camara-deployment.yaml
kubectl get hpa camara-mcp-hpa

# Test scaling
kubectl run -it --rm load-generator --image=busybox --restart=Never -- /bin/sh
# Inside pod: while true; do wget -q -O- http://camara-mcp-service:8000/health; done
```

### Rolling Updates

```bash
# Update image
kubectl set image deployment/camara-mcp \
  camara-mcp=your-registry/camara-mcp:v1.1.0

# Check rollout status
kubectl rollout status deployment/camara-mcp

# Rollback if needed
kubectl rollout undo deployment/camara-mcp
```

### Troubleshooting

```bash
# Pod status
kubectl describe pod <pod-name>

# Logs
kubectl logs -l app=camara-mcp --tail=100

# Shell into pod
kubectl exec -it <pod-name> -- /bin/bash

# Events
kubectl get events --sort-by=.metadata.creationTimestamp

# Resources
kubectl top pods -l app=camara-mcp
kubectl top nodes
```

---

## Production Best Practices

### 1. High Availability

```yaml
# k8s/camara-deployment.yaml
spec:
  replicas: 3  # Minimum for HA
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero downtime
```

### 2. Resource Limits

```yaml
resources:
  requests:
    cpu: "100m"      # Minimum guaranteed
    memory: "128Mi"
  limits:
    cpu: "500m"      # Maximum allowed
    memory: "512Mi"
```

### 3. Security

**Non-root user:**
```dockerfile
USER mcpuser
```

**Read-only filesystem:**
```yaml
securityContext:
  readOnlyRootFilesystem: true
```

**Network policies:**
```bash
kubectl apply -f k8s/network-policy.yaml
```

### 4. Monitoring

**Prometheus metrics:**
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

**Health checks:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

### 5. Secrets Management

**Use external secrets:**
```bash
# AWS Secrets Manager
kubectl create secret generic camara-secrets \
  --from-literal=api-key=$(aws secretsmanager get-secret-value \
    --secret-id camara-api-key --query SecretString --output text)
```

---

## Monitoring & Logging

### Prometheus Metrics

```bash
# Deploy Prometheus
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# Create ServiceMonitor
kubectl apply -f k8s/camara-servicemonitor.yaml
```

### Grafana Dashboard

```bash
# Import dashboard
# Dashboard ID: coming soon
```

### Logging

**Centralized logging (ELK Stack):**
```yaml
# Fluent Bit sidecar
- name: fluent-bit
  image: fluent/fluent-bit:latest
  volumeMounts:
  - name: logs
    mountPath: /app/logs
```

**CloudWatch (AWS):**
```bash
# Install AWS CloudWatch agent
kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/quickstart/cwagent-fluentd-quickstart.yaml
```

### Alerting

**Prometheus AlertManager rules:**
```yaml
groups:
- name: camara-mcp
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status="500"}[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate on CAMARA MCP"
```

---

## Performance Tuning

### Docker

```bash
# Increase memory limit
docker run -d --memory=2g --cpus=2 camara-mcp:latest
```

### Kubernetes

```yaml
# Increase replicas for high traffic
spec:
  replicas: 10

  # Tune HPA
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50  # Scale earlier
```

### Application

```python
# Increase httpx pool size
client = httpx.AsyncClient(
    timeout=TIMEOUT,
    limits=httpx.Limits(max_connections=100)
)
```

---

## Backup & Recovery

### Configuration Backup

```bash
# Backup secrets
kubectl get secret camara-secrets -o yaml > backup-secrets.yaml

# Backup configmap
kubectl get configmap camara-config -o yaml > backup-config.yaml
```

### Disaster Recovery

```bash
# Restore from backup
kubectl apply -f backup-secrets.yaml
kubectl apply -f backup-config.yaml
kubectl rollout restart deployment/camara-mcp
```

---

## Support

- **Docker Issues:** Check container logs: `docker logs camara-mcp`
- **K8s Issues:** Check pod events: `kubectl describe pod <pod-name>`
- **Performance:** Check metrics: `kubectl top pods`

---

**Production-ready deployment for CAMARA FastMCP Server**

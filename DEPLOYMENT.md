# SafetyMind Deployment Guide

This guide covers various deployment options for SafetyMind in production environments.

## 🚀 Quick Start

### 1. Docker Deployment (Recommended)

```bash
# Copy and configure environment
cp env.production.template .env.production
# Edit .env.production with your settings

# Deploy using Docker
./deploy.sh deploy
```

### 2. Docker Compose Deployment (With PostgreSQL/Redis)

```bash
# Deploy with PostgreSQL and Redis
./deploy.sh compose
```

### 3. Kubernetes Deployment

```bash
# Apply Kubernetes configuration
kubectl apply -f k8s-deployment.yaml
```

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Required API keys:
  - ElevenLabs API key
  - Groq API key
  - Mem0 API key (optional)

## 🔧 Configuration

### Environment Variables

Copy `env.production.template` to `.env.production` and configure:

```bash
# Required API Keys
ELEVENLABS_API_KEY=your_elevenlabs_api_key
GROQ_API_KEY=your_groq_api_key
MEM0_API_KEY=your_mem0_api_key

# Database Configuration
DATABASE_URL=sqlite:///app/safetymind.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/safetymind

# Security
SECRET_KEY=your-super-secret-key
ALLOWED_HOSTS=localhost,your-domain.com
```

### Production Settings

- **Workers**: Set `SAFETYMIND_WORKERS=4` for production
- **Log Level**: Use `INFO` or `WARNING` for production
- **Debug**: Set `DEBUG=false` for production
- **CORS**: Configure `CORS_ORIGINS` for your frontend domains

## 🐳 Docker Deployment

### Single Container Deployment

```bash
# Build and run
docker build -t safetymind:latest .
docker run -d \
  --name safetymind-app \
  -p 8000:8000 \
  --env-file .env.production \
  -v $(pwd)/data:/app/data \
  safetymind:latest
```

### Multi-Container Deployment (Docker Compose)

```bash
# Start all services
docker-compose up -d

# Start with PostgreSQL and Redis
docker-compose --profile production up -d
```

## ☸️ Kubernetes Deployment

### Basic Deployment

```bash
# Apply configuration
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods -l app=safetymind
kubectl get services
```

### Custom Configuration

1. Update `k8s-deployment.yaml` with your image registry
2. Configure secrets with your API keys
3. Adjust resource limits and replicas as needed

## 🌐 Cloud Platform Deployment

### AWS ECS

1. Build and push image to ECR
2. Create ECS task definition
3. Configure load balancer
4. Set up RDS for PostgreSQL

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/safetymind
gcloud run deploy safetymind \
  --image gcr.io/PROJECT_ID/safetymind \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
# Deploy to Azure
az container create \
  --resource-group myResourceGroup \
  --name safetymind \
  --image safetymind:latest \
  --ports 8000 \
  --environment-variables \
    SAFETYMIND_HOST=0.0.0.0 \
    SAFETYMIND_PORT=8000
```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up HTTPS/TLS certificates
- [ ] Configure firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Regular security updates

### Database Security

- Use strong passwords for PostgreSQL
- Enable SSL/TLS for database connections
- Regular database backups
- Access control and user permissions

## 📊 Monitoring and Logging

### Health Checks

The application includes health check endpoints:

- `GET /` - Basic health check
- `GET /docs` - API documentation
- `GET /reports` - Data availability check

### Logging

Logs are written to:
- Console output (for containers)
- File: `/app/logs/safetymind.log`
- Configurable log levels: DEBUG, INFO, WARNING, ERROR

### Monitoring Integration

- **Prometheus**: Metrics endpoint available
- **Grafana**: Dashboard templates provided
- **Sentry**: Error tracking integration
- **ELK Stack**: Log aggregation support

## 🔄 Backup and Recovery

### Database Backup

```bash
# SQLite backup
cp /app/data/safetymind.db /backup/safetymind-$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump $DATABASE_URL > /backup/safetymind-$(date +%Y%m%d).sql
```

### Automated Backups

Configure cron job for regular backups:

```bash
# Daily backup at 2 AM
0 2 * * * /app/scripts/backup.sh
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   # Kill process or use different port
   ```

2. **Database Connection Issues**
   ```bash
   # Check database URL format
   echo $DATABASE_URL
   # Test connection
   python -c "from safetymind.storage import init_db; init_db()"
   ```

3. **API Key Issues**
   ```bash
   # Verify API keys are set
   echo $ELEVENLABS_API_KEY
   echo $GROQ_API_KEY
   ```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
export DEBUG=true
export SAFETYMIND_LOG_LEVEL=DEBUG
```

### Container Logs

```bash
# View container logs
docker logs safetymind-app

# Follow logs in real-time
docker logs -f safetymind-app
```

## 📈 Performance Optimization

### Production Optimizations

- Use multiple workers (`SAFETYMIND_WORKERS=4`)
- Enable Redis caching
- Use PostgreSQL instead of SQLite
- Configure CDN for static assets
- Enable gzip compression
- Set up load balancing

### Resource Requirements

**Minimum:**
- CPU: 250m
- Memory: 512Mi
- Storage: 1Gi

**Recommended:**
- CPU: 500m
- Memory: 1Gi
- Storage: 10Gi

## 🔄 Updates and Maintenance

### Rolling Updates

```bash
# Docker Compose
docker-compose pull
docker-compose up -d

# Kubernetes
kubectl rollout restart deployment/safetymind
```

### Database Migrations

```bash
# Run migrations
python migrate_db.py
```

## 📞 Support

For deployment issues:

1. Check logs: `docker logs safetymind-app`
2. Verify configuration: `.env.production`
3. Test health endpoint: `curl http://localhost:8000/`
4. Review this documentation

## 🎯 Next Steps

After successful deployment:

1. Configure your domain and SSL certificates
2. Set up monitoring and alerting
3. Configure automated backups
4. Set up CI/CD pipeline
5. Train users on the new system
6. Plan regular maintenance schedule

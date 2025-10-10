# SaaS Services Telemetry Agent

The SaaS Services Telemetry Agent automatically collects cost and usage metrics from popular SaaS and PaaS platforms.

## Supported Services

### Production-Ready Integrations

1. **MongoDB Atlas** - Database clusters, storage, data transfer
2. **Redis Cloud** - Database instances, throughput, subscriptions
3. **Confluent Kafka** ✨ NEW - Kafka clusters, topics, connectors
4. **Elasticsearch/Elastic Cloud** ✨ NEW - Clusters, storage, shards
5. **GitHub Actions** - Workflow minutes, storage usage
6. **Vercel** ✨ NEW - Deployments, bandwidth, serverless functions
7. **Docker Hub** ✨ NEW - Container pulls, storage, repositories
8. **DataDog** - Hosts, custom metrics, monitoring costs

## Installation

```bash
# Install OpenFinOps with required dependencies
pip install openfinops requests

# Navigate to agents directory
cd agents/
```

## Configuration

### Create Configuration File

```bash
# Generate sample configuration
python saas_services_telemetry_agent.py --create-config saas_config.json
```

### Configure Individual Services

Edit `saas_config.json` to enable and configure services:

```json
{
  "mongodb_atlas": {
    "enabled": true,
    "public_key": "your_public_key",
    "private_key": "your_private_key",
    "project_id": "your_project_id"
  },
  "redis_cloud": {
    "enabled": true,
    "api_key": "your_api_key",
    "secret_key": "your_secret_key",
    "account_id": "your_account_id"
  },
  "confluent_kafka": {
    "enabled": true,
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "cloud_api_key": "optional_cloud_api_key"
  },
  "elasticsearch": {
    "enabled": true,
    "cloud_id": "your_cloud_id",
    "api_key": "your_api_key"
  },
  "github_actions": {
    "enabled": true,
    "token": "ghp_your_token",
    "org_name": "your_org"
  },
  "vercel": {
    "enabled": true,
    "token": "your_vercel_token",
    "team_id": "optional_team_id"
  },
  "docker_hub": {
    "enabled": true,
    "username": "your_username",
    "password": "your_password",
    "organization": "optional_org_name"
  },
  "datadog": {
    "enabled": true,
    "api_key": "your_api_key",
    "app_key": "your_app_key"
  }
}
```

## Running the Agent

### Continuous Mode (Production)

```bash
python saas_services_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --config saas_config.json \
  --interval 3600
```

### Background Mode

```bash
# Run in background
nohup python saas_services_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --config saas_config.json > saas_agent.log 2>&1 &
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY agents/saas_services_telemetry_agent.py .
COPY saas_config.json .

RUN pip install requests

CMD ["python", "saas_services_telemetry_agent.py", \
     "--openfinops-endpoint", "http://openfinops-server:8080", \
     "--config", "saas_config.json", \
     "--interval", "3600"]
```

## Service-Specific Documentation

### MongoDB Atlas

**Authentication:**
- Public Key and Private Key from Atlas API Access
- Project ID from Atlas project settings

**Metrics Collected:**
- Cluster configurations and pricing
- Instance sizes and node counts
- Replication factor
- Cloud provider and region
- Daily and monthly cost estimates

**Pricing Model:**
- Hourly rates based on instance size (M10-M300)
- Multiplied by shards and replication factor

### Redis Cloud

**Authentication:**
- API Key and Secret Key from Redis Cloud dashboard
- Account ID

**Metrics Collected:**
- Subscription details
- Database count per subscription
- Cloud provider and region
- Monthly cost estimates

### Confluent Kafka ✨ NEW

**Authentication:**
- API Key and API Secret from Confluent Cloud
- Optional: Cloud API Key for advanced metrics

**Metrics Collected:**
- Cluster configurations (Basic, Standard, Dedicated)
- Cloud provider and region
- CKU (Capacity Units) for dedicated clusters
- Topic and connector counts
- Hourly and daily cost estimates

**Pricing Tiers:**
- Basic: $0.11/hour
- Standard: $0.45/hour
- Dedicated: $1.50/hour per CKU

**Example Output:**
```json
{
  "service": "confluent_kafka",
  "total_clusters": 3,
  "total_daily_cost_usd": 42.24,
  "clusters": [
    {
      "cluster_id": "lkc-abc123",
      "cluster_name": "production-kafka",
      "cluster_type": "dedicated",
      "cloud_provider": "AWS",
      "region": "us-west-2",
      "cku": 2,
      "status": "RUNNING",
      "hourly_cost_usd": 3.0,
      "daily_cost_usd": 72.0
    }
  ]
}
```

### Elasticsearch/Elastic Cloud ✨ NEW

**Authentication:**
- Cloud ID from Elastic Cloud deployment
- API Key from Elasticsearch

**Metrics Collected:**
- Deployment configurations
- Memory per node (GB)
- Instance count
- Total memory allocation
- Region and version
- Health status
- Daily cost estimates

**Pricing Model:**
- Estimated $0.10 per GB-hour
- Calculated from memory allocation and instance count

**Example Output:**
```json
{
  "service": "elasticsearch_cloud",
  "total_deployments": 2,
  "total_daily_cost_usd": 48.0,
  "deployments": [
    {
      "deployment_id": "deployment-123",
      "name": "production-search",
      "memory_per_node_gb": 8.0,
      "instance_count": 3,
      "total_memory_gb": 24.0,
      "region": "us-east-1",
      "version": "8.11.0",
      "healthy": true,
      "daily_cost_usd": 57.6
    }
  ]
}
```

### GitHub Actions

**Authentication:**
- GitHub Personal Access Token with `read:org` and `read:billing` permissions
- Organization name

**Metrics Collected:**
- Total workflow minutes used
- Included minutes (free tier)
- Billable minutes
- Monthly cost estimates ($0.008/minute for Linux)

### Vercel ✨ NEW

**Authentication:**
- Vercel API token
- Optional: Team ID for team accounts

**Metrics Collected:**
- Project count
- Deployment count (last 30 days)
- Estimated bandwidth usage
- Estimated function invocations
- Monthly cost estimates

**Pricing Estimates:**
- Bandwidth: $20 per 100GB
- Function invocations: $40 per 1M invocations (above free tier)

**Example Output:**
```json
{
  "service": "vercel",
  "total_projects": 15,
  "total_deployments_30d": 127,
  "estimated_bandwidth_gb": 150,
  "estimated_invocations": 1500000,
  "estimated_monthly_cost_usd": 50.0,
  "projects": [
    {
      "id": "prj_abc123",
      "name": "production-app",
      "framework": "nextjs",
      "updated_at": 1706198400000
    }
  ]
}
```

### Docker Hub ✨ NEW

**Authentication:**
- Docker Hub username and password
- Optional: Organization name

**Metrics Collected:**
- Repository count (public and private)
- Total pull count across all repos
- Star count
- Top repositories by pull count
- Monthly cost estimates ($7/month per private repo)

**Example Output:**
```json
{
  "service": "docker_hub",
  "total_repositories": 25,
  "private_repositories": 8,
  "total_pull_count": 1250000,
  "total_star_count": 1523,
  "estimated_monthly_cost_usd": 56.0,
  "top_repositories": [
    {
      "name": "api-server",
      "pull_count": 450000,
      "star_count": 523,
      "is_private": true,
      "last_updated": "2025-01-25T10:30:00Z"
    }
  ]
}
```

### DataDog

**Authentication:**
- API Key and Application Key from DataDog dashboard

**Metrics Collected:**
- Maximum host count (current month)
- Estimated monthly cost ($15/host)
- Usage period

## API Integration

The agent sends telemetry data to OpenFinOps using the standard telemetry ingestion endpoint:

```http
POST /api/v1/telemetry/ingest
Content-Type: application/json

{
  "agent_id": "saas-services-1706198400",
  "timestamp": 1706198400.0,
  "metrics": {
    "timestamp": 1706198400.0,
    "agent_id": "saas-services-1706198400",
    "services": {
      "confluent_kafka": { /* Kafka metrics */ },
      "vercel": { /* Vercel metrics */ },
      "docker_hub": { /* Docker Hub metrics */ },
      "elasticsearch": { /* Elasticsearch metrics */ }
    },
    "summary": {
      "total_services": 8,
      "total_monthly_cost_usd": 3542.50,
      "total_daily_cost_usd": 118.08,
      "estimated_annual_cost_usd": 42510.00
    }
  },
  "agent_health": {
    "status": "healthy",
    "uptime": 86400,
    "last_collection": 1706198400.0
  }
}
```

## Cost Tracking

All costs are automatically sent to the OpenFinOps CostObservatory:

```python
# Costs are automatically attributed
{
  "provider": "saas",
  "service": "confluent_kafka",  # or vercel, docker_hub, elasticsearch
  "cost_usd": 72.00,
  "resource_id": "lkc-abc123",
  "region": "us-west-2",
  "tags": {
    "saas_type": "messaging",
    "cluster_type": "dedicated"
  }
}
```

## Monitoring and Alerts

### View Metrics in OpenFinOps Dashboard

```bash
# Access web UI
http://localhost:8080/dashboard/saas

# View cost summary
curl http://localhost:8080/api/v1/costs/summary?provider=saas
```

### Set Up Cost Alerts

```python
from openfinops.observability import CostObservatory
from openfinops.observability.cost_observatory import Budget

cost_obs = CostObservatory()

# Create budget for SaaS services
budget = Budget(
    budget_id="saas-monthly",
    name="SaaS Services Monthly Budget",
    amount=5000.0,
    period="monthly",
    alert_threshold=0.80,
    scope={
        "provider": "saas"
    }
)

cost_obs.create_budget(budget)
```

## Troubleshooting

### Agent Not Connecting

```bash
# Test endpoint connectivity
curl http://localhost:8080/api/v1/health

# Check agent logs
tail -f saas_agent.log
```

### API Authentication Errors

**Confluent Kafka:**
- Verify API key and secret at https://confluent.cloud/settings/api-keys
- Ensure key has proper permissions (CloudClusterAdmin)

**Vercel:**
- Generate token at https://vercel.com/account/tokens
- Token needs read access to projects and deployments

**Docker Hub:**
- Use Docker Hub personal access token instead of password
- Create at https://hub.docker.com/settings/security

**Elasticsearch:**
- Get API key from Kibana → Stack Management → API Keys
- Ensure deployment ID is correct

### Missing Metrics

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

python saas_services_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --config saas_config.json
```

## Best Practices

1. **Credential Security:**
   - Use environment variables for sensitive credentials
   - Never commit config files with real credentials
   - Use secret management (Vault, AWS Secrets Manager)

2. **Collection Frequency:**
   - Default: 1 hour (3600 seconds)
   - Minimum recommended: 15 minutes (900 seconds)
   - Don't set below API rate limits

3. **High Availability:**
   - Run agent in Docker with restart policy
   - Use orchestration (Kubernetes, ECS) for reliability
   - Monitor agent health via telemetry API

4. **Cost Optimization:**
   - Review service utilization monthly
   - Identify unused or underutilized services
   - Use OpenFinOps recommendations for optimization

## Example: Complete Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  saas-agent:
    build: .
    environment:
      - OPENFINOPS_ENDPOINT=http://openfinops-server:8080
    volumes:
      - ./saas_config.json:/app/saas_config.json:ro
    restart: unless-stopped
    depends_on:
      - openfinops-server

  openfinops-server:
    image: openfinops/openfinops:latest
    ports:
      - "8080:8080"
    restart: unless-stopped
```

```bash
# Deploy
docker-compose up -d

# View logs
docker-compose logs -f saas-agent

# Check metrics
curl http://localhost:8080/api/v1/agents/status
```

## Next Steps

- Set up [cost attribution](../tutorials/cost-attribution.md) for SaaS services
- Configure [budget alerts](../guides/alerting.md) for overspending
- Create [custom dashboards](../tutorials/custom-dashboards.md) for SaaS metrics
- Integrate with [FinOps-as-Code](../api/iac-api.md) for policy enforcement

## Support

For issues or questions:
- GitHub Issues: https://github.com/rdmurugan/OpenFinOps/issues
- Documentation: https://github.com/rdmurugan/OpenFinOps/tree/master/docs

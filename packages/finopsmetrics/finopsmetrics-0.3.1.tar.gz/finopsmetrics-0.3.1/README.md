# FinOpsMetrics - Community Edition

**Free, Proprietary FinOps Platform for AI/ML Cost Observability**

FinOpsMetrics Community Edition is a powerful, free-to-use platform for real-time cost monitoring, tracking, and optimization across multi-cloud environments and AI/ML workloads.

## 🎯 Key Features

### Multi-Cloud Cost Observability
- **AWS Integration**: EC2, EKS, Lambda, RDS, S3, CloudWatch, Cost Explorer
- **Azure Integration**: VMs, AKS, Functions, SQL Database, Monitor, Cost Management
- **GCP Integration**: Compute Engine, GKE, Cloud Functions, Cloud SQL, Monitoring, Billing
- Real-time telemetry collection via agent-based architecture

### AI/ML Workload Monitoring
- LLM training cost tracking
- RAG pipeline observability
- Agent workflow metrics
- GPU utilization monitoring
- Model training performance analytics

### Infrastructure as Code (IaC) Cost Analysis
- Terraform cost estimation
- CloudFormation analysis
- ARM template evaluation
- Pre-deployment cost forecasting

### SaaS & Third-Party Service Tracking
- OpenAI API cost monitoring
- Anthropic Claude API tracking
- Custom API integrations
- Multi-provider cost aggregation

### Advanced Cost Management
- ML-powered anomaly detection
- Tag-based cost attribution
- Budget policies and alerts
- Cost allocation and chargeback
- Custom plugin framework

### VizlyChart Visualization Library
- 15+ chart types (line, bar, scatter, candlestick, radar, heatmap, treemap, etc.)
- Real-time data streaming
- Interactive dashboards
- Financial time-series charts
- GPU-accelerated rendering (optional)
- Export to PNG, SVG, HTML

## 📦 Installation

### Basic Installation
```bash
pip install finopsmetrics
```

### With Cloud Provider Support
```bash
# AWS
pip install finopsmetrics[aws]

# Azure
pip install finopsmetrics[azure]

# GCP
pip install finopsmetrics[gcp]

# All cloud providers
pip install finopsmetrics[all]
```

### Development Installation
```bash
git clone <your-private-repo>
cd finopsmetrics-community
pip install -e ".[dev]"
```

## 🚀 Quick Start

### 1. Start the Observability Server
```bash
finopsmetrics-server --host 127.0.0.1 --port 8080
```

### 2. Deploy Telemetry Agents
```python
from agents.aws_telemetry_agent import AWSTelemetryAgent

# AWS agent automatically discovers resources and calculates costs
agent = AWSTelemetryAgent(
    openfinops_endpoint="http://localhost:8080",
    aws_region="us-west-2"
)
agent.run_continuous(interval_seconds=300)
```

### 3. Query Cost Data
```python
from finopsmetrics.observability import CostObservatory

cost_obs = CostObservatory()
summary = cost_obs.get_cost_summary(time_range_hours=24)

print(f"Total cost (24h): ${summary['total_cost_usd']:.2f}")
print(f"Top service: {summary['top_services'][0]}")
```

### 4. Create Visualizations
```python
from finopsmetrics.vizlychart import LineChart

chart = LineChart(
    title="Daily Cloud Costs",
    x_label="Date",
    y_label="Cost ($)"
)
chart.add_series(dates, costs, label="AWS", color="blue")
chart.render()
chart.save("costs.png")
```

## 🎨 VizlyChart Examples

```python
# Financial candlestick chart
from finopsmetrics.vizlychart import CandlestickChart

chart = CandlestickChart(title="Cost Trends")
chart.add_data(dates, opens, highs, lows, closes)
chart.render()

# Heatmap for resource utilization
from finopsmetrics.vizlychart import HeatmapChart

chart = HeatmapChart(title="CPU Utilization")
chart.add_data(matrix_data, x_labels=hours, y_labels=servers)
chart.render()

# Real-time streaming chart
from finopsmetrics.vizlychart import RealtimeChart

chart = RealtimeChart(title="Live Metrics", buffer_size=100)
chart.start_stream(data_source, update_interval=1.0)
```

## 🏗️ Architecture

FinOpsMetrics uses an **agent-based architecture**:

1. **Telemetry Agents** (separate processes) deployed in cloud accounts
2. Agents automatically discover resources via cloud provider APIs
3. Agents query metrics (CPU, memory, network) and calculate costs
4. Agents send data to ObservabilityHub via REST API
5. **ObservabilityHub** receives and processes telemetry
6. **CostObservatory** aggregates costs, tracks budgets, triggers alerts
7. **Dashboards** display real-time metrics and visualizations

## 📊 Available Commands

```bash
# Start observability server
finopsmetrics-server --port 8080

# View CLI help
finopsmetrics --help

# Run with custom configuration
finopsmetrics-server --config /path/to/config.yaml
```

## 🔌 Plugin System

Create custom plugins to extend functionality:

```python
from finopsmetrics.plugins import BasePlugin

class CustomCostPlugin(BasePlugin):
    def process_cost_entry(self, entry):
        # Custom cost processing logic
        return modified_entry

    def generate_report(self):
        # Custom reporting
        pass
```

Register plugins in `config.yaml`:
```yaml
plugins:
  - module: my_plugins.custom_cost
    class: CustomCostPlugin
    enabled: true
```

## 🔐 License

**Proprietary - Free Community Edition**

FinOpsMetrics Community Edition is **free to use** for personal and commercial purposes under the following conditions:

✅ **Permitted:**
- Install and use for any lawful purpose
- Use in production environments
- Commercial use without fees
- Evaluation and testing

❌ **Restricted:**
- No reverse engineering or decompilation
- No redistribution, sale, or sublicense
- No derivative works
- No use to build competing products
- No source code access beyond distributed form

See [LICENSE](LICENSE) for complete terms.

## 🚀 Upgrade to Enterprise

For advanced features, upgrade to **FinOpsMetrics Enterprise**:

- AI-powered cost optimization recommendations
- Advanced analytics and forecasting
- Workspace collaboration features
- Version control for budgets and policies
- GIS-based regional analysis
- GPU-accelerated processing
- Priority support

Contact: durai@infinidatum.net

## 📚 Documentation

- **Installation Guide**: See above
- **API Reference**: Coming soon
- **Telemetry Agent Setup**: See `agents/README.md`
- **VizlyChart Gallery**: See `examples/vizlychart/`

## 🤝 Support

- **Issues**: Contact durai@infinidatum.net
- **Commercial Licensing**: durai@infinidatum.net
- **Enterprise Sales**: durai@infinidatum.net

## 📈 Roadmap

- [ ] Kubernetes cost attribution
- [ ] Enhanced ML model training tracking
- [ ] GraphQL API
- [ ] Mobile dashboard app
- [ ] Advanced FinOps best practice recommendations

---

**FinOpsMetrics** - Intelligent Cost Observability for Cloud and AI/ML Workloads

Copyright © 2025 Infinidatum. All rights reserved.

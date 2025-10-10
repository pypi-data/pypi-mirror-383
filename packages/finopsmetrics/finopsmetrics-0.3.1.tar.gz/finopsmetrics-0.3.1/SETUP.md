# FinOpsMetrics Community Edition - Setup Instructions

## Repository Setup

### 1. Create Private GitHub Repository

```bash
# Create a new private repository on GitHub
# Repository name: finopsmetrics-community
# Description: FinOpsMetrics Community Edition - Free FinOps Platform
# Visibility: Private
```

### 2. Initialize Git and Push

```bash
cd /path/to/finopsmetrics-community

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: FinOpsMetrics Community Edition v0.3.0

- Core observability system (ObservabilityHub, CostObservatory, LLMObservabilityHub)
- Multi-cloud telemetry agents (AWS, Azure, GCP)
- IaC cost analysis (Terraform, CloudFormation, ARM)
- SaaS tracking (OpenAI, Anthropic, MongoDB Atlas, etc.)
- ML anomaly detection
- Tag-based cost attribution
- Budget policies and alerts
- Plugin framework
- VizlyChart visualization library (15+ chart types)
- Real-time streaming charts
- Proprietary license (Free Community Edition)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Add remote (replace with your actual repository URL)
git remote add origin git@github.com:yourusername/finopsmetrics-community.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Development Setup

### 1. Clone Repository

```bash
git clone git@github.com:yourusername/finopsmetrics-community.git
cd finopsmetrics-community
```

### 2. Create Virtual Environment

```bash
# Using venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n finopsmetrics python=3.11
conda activate finopsmetrics
```

### 3. Install in Development Mode

```bash
# Basic installation
pip install -e .

# With development tools
pip install -e ".[dev]"

# With all cloud providers
pip install -e ".[all]"

# With specific cloud providers
pip install -e ".[aws,azure,gcp]"
```

### 4. Verify Installation

```bash
# Check version
python -c "import finopsmetrics; print(finopsmetrics.__version__)"

# Run tests
pytest

# Check CLI
finopsmetrics --help
finopsmetrics-server --help
```

## Building Distribution

### 1. Install Build Tools

```bash
pip install build twine
```

### 2. Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ src/finopsmetrics.egg-info/

# Build wheel and source distribution
python -m build
```

### 3. Check Distribution

```bash
twine check dist/*
```

### 4. Upload to PyPI

```bash
# Test PyPI (optional)
twine upload --repository testpypi dist/*

# Production PyPI
twine upload dist/*
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# Visualization tests
pytest -m visualization

# Fast tests (exclude slow)
pytest -m "not slow"
```

### Run with Coverage

```bash
pytest --cov=src/finopsmetrics --cov-report=html --cov-report=term
```

## Code Quality

### Format Code

```bash
black src/ tests/
```

### Lint Code

```bash
ruff check src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Configuration

### Create Configuration File

```bash
# Create config directory
mkdir -p ~/.finopsmetrics

# Create config file
cat > ~/.finopsmetrics/config.yaml << EOF
observability:
  host: "0.0.0.0"
  port: 8080

telemetry:
  collection_interval: 300  # seconds
  retention_days: 90

budgets:
  default_currency: "USD"
  alert_threshold: 0.8  # 80%

plugins:
  enabled: true
  directory: "~/.finopsmetrics/plugins"
EOF
```

## Running the System

### Start Observability Server

```bash
finopsmetrics-server --port 8080
```

### Deploy Telemetry Agents

```bash
# AWS Agent
python agents/aws_telemetry_agent.py \
  --endpoint http://localhost:8080 \
  --region us-west-2 \
  --interval 300

# Azure Agent
python agents/azure_telemetry_agent.py \
  --endpoint http://localhost:8080 \
  --subscription-id YOUR_SUBSCRIPTION_ID \
  --interval 300

# GCP Agent
python agents/gcp_telemetry_agent.py \
  --endpoint http://localhost:8080 \
  --project-id YOUR_PROJECT_ID \
  --interval 300
```

## Directory Structure

```
finopsmetrics-community/
├── src/
│   └── finopsmetrics/
│       ├── __init__.py
│       ├── cli.py
│       ├── observability/       # Core observability
│       ├── multicloud/          # AWS, Azure, GCP
│       ├── iac/                 # Infrastructure as Code
│       ├── saas/                # SaaS services
│       ├── ml/                  # ML features
│       ├── tagging/             # Cost attribution
│       ├── policy/              # Budget policies
│       ├── plugins/             # Plugin framework
│       ├── vizlychart/          # Visualization library
│       ├── config/              # Configuration
│       └── database/            # Database utilities
├── agents/                      # Telemetry agents
├── tests/                       # Test suite
├── examples/                    # Example code
├── docs/                        # Documentation
├── pyproject.toml               # Package metadata
├── LICENSE                      # Proprietary license
├── README.md                    # Main documentation
└── SETUP.md                     # This file
```

## Updating Version

### 1. Update Version Number

Edit `pyproject.toml`:
```toml
version = "0.3.1"
```

Edit `src/finopsmetrics/__init__.py`:
```python
__version__ = "0.3.1"
```

### 2. Create Release

```bash
# Commit version bump
git add pyproject.toml src/finopsmetrics/__init__.py
git commit -m "Bump version to 0.3.1"

# Create tag
git tag -a v0.3.1 -m "Release v0.3.1"

# Push
git push origin main --tags

# Build and upload to PyPI
python -m build
twine upload dist/*
```

## Troubleshooting

### Import Errors

```bash
# Reinstall in development mode
pip install -e .
```

### Test Failures

```bash
# Run specific test with verbose output
pytest tests/test_observability.py -v

# Run with debug output
pytest --log-cli-level=DEBUG
```

### Cloud Provider Credentials

```bash
# AWS
export AWS_PROFILE=your-profile
aws configure

# Azure
az login

# GCP
gcloud auth application-default login
```

## Support

For issues and questions:
- Email: durai@infinidatum.net
- Repository Issues: GitHub Issues (private repo)

## License

FinOpsMetrics Community Edition
Copyright © 2025 Infinidatum. All rights reserved.

See LICENSE file for complete terms.

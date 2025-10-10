# FinOpsMetrics Dashboard - Setup Instructions

## Repository Setup

### 1. Create Private GitHub Repository

```bash
# Create a new private repository on GitHub
# Repository name: finopsmetrics-dashboard
# Description: FinOpsMetrics Dashboard - Web UI for FinOps Cost Monitoring
# Visibility: Private
```

### 2. Initialize Git and Push

```bash
cd /path/to/finopsmetrics-dashboard

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: FinOpsMetrics Dashboard v0.3.0

- Role-based executive dashboards (CFO, COO, Infrastructure Leader, Finance Analyst)
- Real-time WebSocket updates with Chart.js
- Complete IAM and RBAC system
- User management CLI
- Authentication middleware
- Modern web UI with Flask and Flask-SocketIO
- Dashboard routing and access control
- Alert notifications
- Export and reporting capabilities
- Proprietary license (Free with Community Edition)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Add remote (replace with your actual repository URL)
git remote add origin git@github.com:yourusername/finopsmetrics-dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Development Setup

### Prerequisites

**REQUIRED**: FinOpsMetrics Community Edition must be installed first:

```bash
# Install community edition from PyPI
pip install finopsmetrics

# Or install from local development
cd /path/to/finopsmetrics-community
pip install -e .
```

**OPTIONAL**: For enhanced dashboards, install Enterprise Edition:

```bash
pip install finopsmetrics-enterprise
```

### 1. Clone Repository

```bash
git clone git@github.com:yourusername/finopsmetrics-dashboard.git
cd finopsmetrics-dashboard
```

### 2. Create Virtual Environment

```bash
# Using venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n finopsmetrics-dashboard python=3.11
conda activate finopsmetrics-dashboard
```

### 3. Install in Development Mode

```bash
# Basic installation (requires finopsmetrics)
pip install -e .

# With enterprise features
pip install -e ".[enterprise]"

# With development tools
pip install -e ".[dev]"
```

### 4. Verify Installation

```bash
# Check imports
python -c "from finopsmetrics.dashboard import CFODashboard; print('✓ Dashboard available')"

# Check CLI
finopsmetrics-dashboard --help

# Run tests
pytest
```

## Building Distribution

### 1. Install Build Tools

```bash
pip install build twine
```

### 2. Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ src/finopsmetrics_dashboard.egg-info/

# Build wheel and source distribution
python -m build
```

### 3. Check Distribution

```bash
twine check dist/*
```

### 4. Upload to PyPI or Private Registry

```bash
# Upload to PyPI (public)
twine upload dist/*

# Or upload to private PyPI server
twine upload --repository-url https://your-private-pypi.com dist/*
```

## Initial Configuration

### 1. Setup IAM System

Create first admin user:

```bash
python -m finopsmetrics.dashboard.iam_cli add-user \
  --username admin \
  --email admin@company.com \
  --role admin \
  --password "SecurePassword123!"
```

### 2. Configure IAM Roles

Edit `src/finopsmetrics/dashboard/iam_config.yaml`:

```yaml
roles:
  admin:
    permissions:
      - "*"
    dashboards:
      - all

  cfo:
    permissions:
      - view_financial_dashboard
      - view_budgets
      - view_cost_trends
      - export_reports
      - manage_budgets
    dashboards:
      - cfo_dashboard

  coo:
    permissions:
      - view_operational_dashboard
      - view_service_health
      - view_performance_metrics
    dashboards:
      - coo_dashboard

  infrastructure_leader:
    permissions:
      - view_infrastructure_dashboard
      - view_capacity_planning
      - view_resource_utilization
      - view_technical_metrics
    dashboards:
      - infrastructure_dashboard

  finance_analyst:
    permissions:
      - view_detailed_costs
      - view_cost_attribution
      - create_reports
      - view_forecasts
      - view_variance_analysis
    dashboards:
      - finance_analyst_dashboard

  developer:
    permissions:
      - view_basic_costs
      - view_own_resources
    dashboards:
      - developer_dashboard

authentication:
  session_timeout: 3600  # 1 hour
  max_failed_attempts: 5
  lockout_duration: 900  # 15 minutes

password_policy:
  min_length: 12
  require_uppercase: true
  require_lowercase: true
  require_numbers: true
  require_special: true
```

### 3. Create Dashboard Configuration

Create `dashboard_config.yaml`:

```yaml
dashboard:
  title: "FinOpsMetrics Dashboard"
  logo: "/static/logo.png"
  theme: "light"  # or "dark"

  server:
    host: "0.0.0.0"
    port: 5000
    debug: false

  observability:
    endpoint: "http://localhost:8080"
    api_key: "your-api-key"
    timeout: 30

  features:
    real_time_updates: true
    refresh_interval: 60  # seconds
    export_enabled: true
    alerts_enabled: true
    websocket_enabled: true

  charts:
    default_type: "line"
    color_scheme: "corporate"
    animation_enabled: true

  notifications:
    slack_webhook: "https://hooks.slack.com/services/YOUR/WEBHOOK"
    email_enabled: true
    email_smtp_server: "smtp.company.com"
    email_smtp_port: 587
    email_from: "finops@company.com"

  security:
    https_enabled: false
    ssl_cert: "/path/to/cert.pem"
    ssl_key: "/path/to/key.pem"
    cors_origins:
      - "https://yourapp.com"
```

## Running the Dashboard

### 1. Start Dashboard Server

```bash
# Basic start
finopsmetrics-dashboard

# Custom port
finopsmetrics-dashboard --port 8080

# Custom host and port
finopsmetrics-dashboard --host 0.0.0.0 --port 8080

# With debug mode
finopsmetrics-dashboard --debug

# With custom config
finopsmetrics-dashboard --config /path/to/dashboard_config.yaml
```

### 2. Access Dashboard

Open browser to:
- **Main**: http://localhost:5000
- **CFO Dashboard**: http://localhost:5000/dashboard/cfo
- **COO Dashboard**: http://localhost:5000/dashboard/coo
- **Infrastructure**: http://localhost:5000/dashboard/infrastructure
- **Finance Analyst**: http://localhost:5000/dashboard/finance

### 3. Login

Use credentials created with IAM CLI:
- Username: admin
- Password: SecurePassword123!

## User Management

### Add Users

```bash
# Add CFO
python -m finopsmetrics.dashboard.iam_cli add-user \
  --username john.cfo \
  --email john@company.com \
  --role cfo \
  --password "TempPassword123!"

# Add Finance Analyst
python -m finopsmetrics.dashboard.iam_cli add-user \
  --username jane.analyst \
  --email jane@company.com \
  --role finance_analyst \
  --password "TempPassword456!"

# Add Infrastructure Leader
python -m finopsmetrics.dashboard.iam_cli add-user \
  --username bob.infra \
  --email bob@company.com \
  --role infrastructure_leader \
  --password "TempPassword789!"
```

### List Users

```bash
python -m finopsmetrics.dashboard.iam_cli list-users
```

### Update User Role

```bash
python -m finopsmetrics.dashboard.iam_cli update-user \
  --username jane.analyst \
  --role cfo
```

### Remove User

```bash
python -m finopsmetrics.dashboard.iam_cli remove-user \
  --username bob.infra
```

### Reset Password

```bash
python -m finopsmetrics.dashboard.iam_cli reset-password \
  --username john.cfo \
  --password "NewSecurePassword123!"
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Dashboard-Specific Tests

```bash
# Dashboard tests
pytest tests/test_dashboards.py -v

# IAM tests
pytest tests/test_iam_system.py -v

# Web UI tests
pytest tests/test_webui.py -v
```

### Run with Coverage

```bash
pytest --cov=src/finopsmetrics/dashboard --cov=src/finopsmetrics/webui --cov-report=html
```

## Customization

### Custom Branding

Create custom logo and theme:

```bash
# Copy logo to static directory
mkdir -p src/finopsmetrics/webui/static/images
cp /path/to/company-logo.png src/finopsmetrics/webui/static/images/logo.png

# Update dashboard_config.yaml
# logo: "/static/images/logo.png"
```

### Custom CSS

Edit `src/finopsmetrics/webui/static/dashboard.css`:

```css
:root {
  --primary-color: #0066cc;
  --secondary-color: #ff9900;
  --background-color: #ffffff;
  --text-color: #333333;
}

.dashboard-header {
  background-color: var(--primary-color);
  color: white;
}
```

### Custom Dashboard Templates

Create custom template in `src/finopsmetrics/webui/templates/`:

```html
<!-- custom_dashboard.html -->
{% extends "base.html" %}

{% block content %}
<div class="dashboard">
  <h1>{{ dashboard_title }}</h1>
  <div class="charts">
    {{ charts | safe }}
  </div>
</div>
{% endblock %}
```

## Production Deployment

### 1. Use Production WSGI Server

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 finopsmetrics.webui.server:app
```

### 2. Enable HTTPS

```bash
# Generate SSL certificate (or use Let's Encrypt)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Run with HTTPS
finopsmetrics-dashboard \
  --host 0.0.0.0 \
  --port 443 \
  --ssl-cert cert.pem \
  --ssl-key key.pem
```

### 3. Setup Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/finopsmetrics

server {
    listen 80;
    server_name finops.company.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name finops.company.com;

    ssl_certificate /etc/ssl/certs/finops.crt;
    ssl_certificate_key /etc/ssl/private/finops.key;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /socket.io {
        proxy_pass http://localhost:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 4. Setup Systemd Service

Create `/etc/systemd/system/finopsmetrics-dashboard.service`:

```ini
[Unit]
Description=FinOpsMetrics Dashboard
After=network.target

[Service]
Type=simple
User=finops
WorkingDirectory=/opt/finopsmetrics
Environment="PATH=/opt/finopsmetrics/venv/bin"
ExecStart=/opt/finopsmetrics/venv/bin/finopsmetrics-dashboard --host 127.0.0.1 --port 5000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable finopsmetrics-dashboard
sudo systemctl start finopsmetrics-dashboard
sudo systemctl status finopsmetrics-dashboard
```

## Directory Structure

```
finopsmetrics-dashboard/
├── src/
│   └── finopsmetrics/
│       ├── __init__.py              # Namespace package
│       ├── dashboard/               # Dashboard components
│       │   ├── __init__.py
│       │   ├── cfo_dashboard.py
│       │   ├── coo_dashboard.py
│       │   ├── infrastructure_leader_dashboard.py
│       │   ├── finance_analyst_dashboard.py
│       │   ├── iam_system.py
│       │   ├── iam_cli.py
│       │   ├── iam_config.yaml
│       │   ├── auth_middleware.py
│       │   └── dashboard_router.py
│       └── webui/                   # Web UI
│           ├── __init__.py
│           ├── server.py
│           ├── templates/           # HTML templates
│           │   ├── base.html
│           │   ├── login.html
│           │   ├── dashboard.html
│           │   └── charts.html
│           └── static/              # CSS, JS, images
│               ├── dashboard.css
│               ├── dashboard.js
│               └── images/
├── tests/                           # Test suite
├── examples/                        # Example code
├── pyproject.toml                   # Package metadata
├── LICENSE                          # Proprietary license
├── README.md                        # Main documentation
└── SETUP.md                         # This file
```

## Integration with ObservabilityHub

The dashboard connects to the FinOpsMetrics observability server:

```python
# In dashboard_config.yaml
observability:
  endpoint: "http://localhost:8080"
  api_key: "your-api-key"
```

### Start Observability Server First

```bash
# Terminal 1: Start observability server
finopsmetrics-server --port 8080

# Terminal 2: Start dashboard
finopsmetrics-dashboard --port 5000
```

## Troubleshooting

### Dashboard Won't Start

```bash
# Check if port is in use
lsof -i :5000

# Kill existing process
kill -9 $(lsof -t -i:5000)

# Start with debug
finopsmetrics-dashboard --debug
```

### No Data Showing

```bash
# Verify observability server is running
curl http://localhost:8080/health

# Check telemetry agents
curl http://localhost:8080/api/v1/telemetry/status

# Check dashboard logs
finopsmetrics-dashboard --debug
```

### WebSocket Connection Issues

```bash
# Check eventlet is installed
pip install eventlet>=0.33.0

# Check CORS settings in dashboard_config.yaml
cors_origins:
  - "http://localhost:5000"
```

### Authentication Errors

```bash
# Reset admin password
python -m finopsmetrics.dashboard.iam_cli reset-password \
  --username admin \
  --password "NewPassword123!"

# Check IAM config
cat src/finopsmetrics/dashboard/iam_config.yaml
```

## Monitoring

### Health Check Endpoint

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.3.0",
  "uptime_seconds": 3600,
  "active_users": 5,
  "observability_hub": "connected"
}
```

### Metrics Endpoint

```bash
curl http://localhost:5000/api/metrics
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
git tag -a v0.3.1 -m "Dashboard Release v0.3.1"

# Push
git push origin main --tags

# Build and upload
python -m build
twine upload dist/*
```

## Support

For support:
- **Issues**: Contact durai@infinidatum.net
- **Enterprise Support**: Available with Enterprise Edition

## License

FinOpsMetrics Dashboard
Copyright © 2025 Infinidatum. All rights reserved.

Proprietary - Free for Use with FinOpsMetrics Community Edition

See LICENSE file for complete terms.

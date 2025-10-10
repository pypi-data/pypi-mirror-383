# FinOpsMetrics Dashboard

**Modern Web UI for FinOps Cost Monitoring & Analytics**

FinOpsMetrics Dashboard provides a modern, role-based web interface for visualizing costs, monitoring infrastructure, and managing budgets across multi-cloud and AI/ML workloads.

## 🎯 Features

### Role-Based Executive Dashboards
- **CFO Dashboard**: Financial overview, budget tracking, cost trends, ROI analysis
- **COO Dashboard**: Operational metrics, service health, efficiency indicators
- **Infrastructure Leader Dashboard**: Resource utilization, capacity planning, technical metrics
- **Finance Analyst Dashboard**: Detailed cost breakdowns, variance analysis, forecasting

### Real-Time Monitoring
- **WebSocket Integration**: Live cost and metric updates
- **Interactive Charts**: Chart.js-powered visualizations
- **Streaming Telemetry**: Real-time infrastructure monitoring
- **Alert Notifications**: In-dashboard alert system

### IAM & Security
- **Role-Based Access Control (RBAC)**: CFO, COO, Finance Analyst, Infrastructure Leader, Developer
- **Authentication Middleware**: Secure login and session management
- **User Management CLI**: Add, remove, and modify user permissions
- **Audit Logging**: Complete audit trail of dashboard access

### Dashboard Capabilities
- **Multi-Cloud Cost Views**: Unified view across AWS, Azure, GCP
- **Budget Tracking**: Visual budget vs. actual comparisons
- **Cost Attribution**: Tag-based cost breakdowns
- **Service Health**: Real-time infrastructure health status
- **Anomaly Detection**: Visual indicators for cost anomalies
- **Export & Reports**: Download charts and generate reports

### Enterprise Features (with Enterprise Edition)
- **Advanced AI Recommendations**: ML-driven optimization suggestions
- **Workspace Collaboration**: Team-based dashboard sharing
- **Version Control**: Track dashboard configuration changes
- **Custom Branding**: White-label dashboards
- **SSO Integration**: Enterprise authentication providers

## 📦 Installation

### Prerequisites
1. **FinOpsMetrics Community Edition** must be installed:
   ```bash
   pip install finopsmetrics
   ```

### Install Dashboard
```bash
pip install finopsmetrics-dashboard
```

### With Enterprise Features (Optional)
```bash
pip install finopsmetrics-dashboard[enterprise]
```

### Development Installation
```bash
git clone <your-private-dashboard-repo>
cd finopsmetrics-dashboard
pip install -e ".[dev]"
```

## 🚀 Quick Start

### 1. Start the Dashboard Server
```bash
finopsmetrics-dashboard
```

The dashboard will be available at: `http://localhost:5000`

### 2. Custom Port and Host
```bash
finopsmetrics-dashboard --host 0.0.0.0 --port 8080
```

### 3. First-Time Setup

Create an admin user:
```bash
python -m finopsmetrics.dashboard.iam_cli add-user \
  --username admin \
  --email admin@company.com \
  --role admin \
  --password SecurePassword123
```

### 4. Access Dashboards

Navigate to:
- **CFO Dashboard**: `http://localhost:5000/dashboard/cfo`
- **COO Dashboard**: `http://localhost:5000/dashboard/coo`
- **Infrastructure Dashboard**: `http://localhost:5000/dashboard/infrastructure`
- **Finance Analyst Dashboard**: `http://localhost:5000/dashboard/finance`

## 🔐 IAM Configuration

### User Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **CFO** | View financials, budgets, ROI | Executive financial oversight |
| **COO** | View operations, service health | Operational management |
| **Infrastructure Leader** | View infrastructure, capacity | Technical leadership |
| **Finance Analyst** | Detailed cost analysis, forecasting | Cost analysis and reporting |
| **Developer** | Limited cost visibility | Development teams |
| **Admin** | Full system access | System administration |

### Manage Users

```bash
# Add user
python -m finopsmetrics.dashboard.iam_cli add-user \
  --username john.doe \
  --email john@company.com \
  --role finance_analyst \
  --password TempPassword123

# List users
python -m finopsmetrics.dashboard.iam_cli list-users

# Update user role
python -m finopsmetrics.dashboard.iam_cli update-user \
  --username john.doe \
  --role cfo

# Remove user
python -m finopsmetrics.dashboard.iam_cli remove-user \
  --username john.doe
```

### IAM Configuration File

Edit `src/finopsmetrics/dashboard/iam_config.yaml`:

```yaml
roles:
  cfo:
    permissions:
      - view_financial_dashboard
      - view_budgets
      - view_cost_trends
      - export_reports
    dashboards:
      - cfo_dashboard

  finance_analyst:
    permissions:
      - view_detailed_costs
      - view_cost_attribution
      - create_reports
      - view_forecasts
    dashboards:
      - finance_analyst_dashboard

  infrastructure_leader:
    permissions:
      - view_infrastructure_metrics
      - view_capacity_planning
      - view_service_health
    dashboards:
      - infrastructure_dashboard
```

## 🎨 Dashboard Customization

### Custom Configuration

Create `dashboard_config.yaml`:

```yaml
dashboard:
  title: "YourCompany FinOps Dashboard"
  logo: "/static/logo.png"
  theme: "dark"  # or "light"

  refresh_interval: 60  # seconds

  charts:
    default_chart_type: "line"
    color_scheme: "corporate"

  features:
    real_time_updates: true
    export_enabled: true
    alerts_enabled: true

  integrations:
    slack_webhook: "https://hooks.slack.com/..."
    email_enabled: true
    email_smtp_server: "smtp.company.com"
```

### Custom Branding (Enterprise Only)

```python
from finopsmetrics.dashboard import DashboardServer

server = DashboardServer(
    branding={
        "company_name": "YourCompany",
        "logo_url": "/static/your-logo.png",
        "primary_color": "#0066cc",
        "secondary_color": "#ff9900"
    }
)
server.run(host="0.0.0.0", port=5000)
```

## 📊 Dashboard Views

### CFO Dashboard
- **Total Cost Overview**: Current month, quarter, year
- **Budget Status**: Budget vs. actual with variance %
- **Cost Trends**: Daily/weekly/monthly cost charts
- **Top Cost Drivers**: Services and resources by cost
- **ROI Metrics**: Cost optimization savings
- **Forecast**: Projected costs for next period

### COO Dashboard
- **Service Health**: Uptime, availability, incidents
- **Operational Efficiency**: Resource utilization rates
- **Performance Metrics**: Response times, throughput
- **Capacity Status**: Available vs. used capacity
- **Cost per Transaction**: Efficiency indicators
- **Team Performance**: Deployment frequency, lead time

### Infrastructure Leader Dashboard
- **Resource Utilization**: CPU, memory, GPU, storage
- **Capacity Planning**: Growth trends and forecasts
- **Infrastructure Health**: Cluster and node status
- **Performance Metrics**: Latency, throughput
- **Scaling Events**: Auto-scaling activity
- **Cost by Resource Type**: EC2, Lambda, RDS, etc.

### Finance Analyst Dashboard
- **Detailed Cost Breakdown**: By service, region, tag
- **Variance Analysis**: Budget vs. actual deep-dive
- **Cost Attribution**: Team, project, environment
- **Trend Analysis**: Historical cost patterns
- **Anomaly Detection**: Cost spike identification
- **Forecast Models**: Multiple forecasting scenarios

## 🔌 API Integration

The dashboard exposes REST APIs for integration:

```python
import requests

# Get dashboard data
response = requests.get(
    "http://localhost:5000/api/dashboard/cfo",
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)
data = response.json()

# Get real-time metrics
response = requests.get(
    "http://localhost:5000/api/metrics/realtime",
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)
metrics = response.json()
```

## 🔧 WebSocket Real-Time Updates

Connect to WebSocket for live updates:

```javascript
// JavaScript client
const socket = io('http://localhost:5000');

socket.on('cost_update', (data) => {
    console.log('New cost data:', data);
    updateChart(data);
});

socket.on('alert', (alert) => {
    console.log('Alert:', alert.message);
    showNotification(alert);
});
```

## 🚦 Health Check

Check dashboard health:

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.3.0",
  "uptime_seconds": 3600,
  "database": "connected",
  "observability_hub": "connected"
}
```

## 🔐 Security

### Authentication

The dashboard supports multiple authentication methods:

1. **Username/Password**: Default authentication
2. **API Keys**: For programmatic access
3. **SSO (Enterprise)**: Okta, Azure AD, Google Workspace

### HTTPS Configuration

For production, enable HTTPS:

```bash
finopsmetrics-dashboard \
  --host 0.0.0.0 \
  --port 443 \
  --ssl-cert /path/to/cert.pem \
  --ssl-key /path/to/key.pem
```

### CORS Configuration

Configure CORS for API access:

```python
from finopsmetrics.dashboard import DashboardServer

server = DashboardServer(
    cors_origins=["https://yourapp.com", "https://admin.yourapp.com"]
)
server.run()
```

## 📱 Mobile Access

The dashboard is mobile-responsive and works on:
- iOS Safari
- Android Chrome
- Mobile browsers

## 🔄 Integration with FinOpsMetrics Server

The dashboard connects to the FinOpsMetrics observability server:

```yaml
# dashboard_config.yaml
observability:
  endpoint: "http://localhost:8080"
  api_key: "your-api-key"
  timeout: 30
```

## 🐛 Troubleshooting

### Dashboard Won't Start
```bash
# Check if port is available
lsof -i :5000

# Start with debug logging
finopsmetrics-dashboard --debug
```

### No Data Showing
```bash
# Verify observability server is running
curl http://localhost:8080/health

# Check telemetry agents are sending data
curl http://localhost:8080/api/v1/telemetry/status
```

### WebSocket Connection Issues
```bash
# Check firewall settings
# Ensure WebSocket port is open
# Verify eventlet is installed
pip install eventlet>=0.33.0
```

## 📚 Documentation

- **Installation Guide**: See above
- **IAM Configuration**: See `iam_config.yaml`
- **API Reference**: Coming soon
- **Customization Guide**: Coming soon

## 🤝 Support

- **Issues**: Contact durai@infinidatum.net
- **Enterprise Support**: Priority support included with Enterprise Edition

## 🔐 License

**Proprietary - Free for Use with FinOpsMetrics Community Edition**

The dashboard is free to use with FinOpsMetrics Community Edition. Enterprise features require FinOpsMetrics Enterprise Edition license.

See [LICENSE](LICENSE) for complete terms.

## 🆚 Community vs. Enterprise Dashboards

| Feature | Community | Enterprise |
|---------|-----------|------------|
| Role-Based Dashboards | ✅ | ✅ |
| Real-Time Updates | ✅ | ✅ |
| Basic IAM | ✅ | ✅ |
| Export Charts | ✅ | ✅ |
| AI Recommendations | ❌ | ✅ |
| Workspace Collaboration | ❌ | ✅ |
| Custom Branding | ❌ | ✅ |
| SSO Integration | ❌ | ✅ |
| Advanced Analytics | ❌ | ✅ |
| Version Control | ❌ | ✅ |

---

**FinOpsMetrics Dashboard** - Modern Web UI for Cloud and AI/ML Cost Observability

Copyright © 2025 Infinidatum. All rights reserved.

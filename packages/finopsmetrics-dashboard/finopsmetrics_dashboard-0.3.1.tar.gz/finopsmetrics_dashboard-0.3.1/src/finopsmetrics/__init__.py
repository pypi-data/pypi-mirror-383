"""
FinOpsMetrics Dashboard - Namespace Package
============================================

This is a namespace package that extends finopsmetrics with dashboard features.
Requires finopsmetrics (Community Edition) to be installed.

Dashboard Features:
- Role-Based Executive Dashboards (CFO, COO, Infrastructure Leader, Finance Analyst)
- Real-Time WebSocket Updates
- IAM and RBAC System
- Interactive Web UI
- Cost Visualization and Reporting
- Alert Notifications

License: Proprietary - Free for Use with FinOpsMetrics
"""

# This is a namespace package that extends finopsmetrics
# Declare as namespace package to allow proper module discovery
__path__ = __import__('pkgutil').extend_path(__path__, __name__)

__version__ = "0.3.1"
__author__ = "FinOpsMetrics Dashboard"
__license__ = "Proprietary"

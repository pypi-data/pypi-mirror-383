"""
Vizly Enterprise Module
=======================

Enterprise-grade visualization and analytics platform with advanced security,
performance, and integration capabilities.

Key Features:
- Enterprise security and compliance
- Advanced GIS and geospatial analytics
- High-performance big data processing
- AI-powered visualization assistance
- Enterprise system integration
- Collaboration and sharing platform
"""

# Copyright (c) 2025 Infinidatum
# Author: Duraimurugan Rajamanickam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



# Core Security Infrastructure
from .security import EnterpriseSecurityManager, ComplianceAuditLogger
from .admin import UserManager, RoleManager, AuditManager
from .licensing import LicenseManager, LicenseEnforcer
from .benchmarks import PerformanceBenchmark

# Enterprise Charts & Visualization
from .charts import (
    EnterpriseBaseChart, ExecutiveDashboardChart, FinancialAnalyticsChart,
    ComplianceChart, RiskAnalysisChart, EnterpriseChartFactory
)
from .themes import (
    EnterpriseTheme, PresentationTheme, PrintTheme, DarkTheme,
    ThemeManager, BrandingConfig, AccessibilityConfig
)
from .exports import EnterpriseExporter, ExportConfig, ReportSection

# Enterprise Server & API
try:
    from .server import EnterpriseServer
except ImportError:
    # Fallback if aiohttp not available
    class EnterpriseServer:
        def __init__(self, *args, **kwargs):
            raise ImportError("aiohttp is required for enterprise server. Install with: pip install aiohttp")

# GIS & Analytics
from .gis import EnterpriseGISEngine, SpatialAnalyticsEngine, RealTimeTracker
from .performance import DistributedDataEngine, GPUAcceleratedRenderer, IntelligentDataSampler, EnterprisePerformanceBenchmark

# Collaboration & AI
from .collaboration import WorkspaceManager, VisualizationVersionControl
from .connectors import EnterpriseDataConnectors
from .ai import VizlyAI, ChartRecommendationEngine

__all__ = [
    # Core Security Infrastructure
    "EnterpriseSecurityManager",
    "ComplianceAuditLogger",
    "UserManager",
    "RoleManager",
    "AuditManager",
    "LicenseManager",
    "LicenseEnforcer",

    # Enterprise Charts & Visualization
    "EnterpriseBaseChart",
    "ExecutiveDashboardChart",
    "FinancialAnalyticsChart",
    "ComplianceChart",
    "RiskAnalysisChart",
    "EnterpriseChartFactory",

    # Themes & Styling
    "EnterpriseTheme",
    "PresentationTheme",
    "PrintTheme",
    "DarkTheme",
    "ThemeManager",
    "BrandingConfig",
    "AccessibilityConfig",

    # Export & Reporting
    "EnterpriseExporter",
    "ExportConfig",
    "ReportSection",

    # Enterprise Server & API
    "EnterpriseServer",

    # Performance & Benchmarking
    "PerformanceBenchmark",
    "DistributedDataEngine",
    "GPUAcceleratedRenderer",
    "IntelligentDataSampler",
    "EnterprisePerformanceBenchmark",

    # GIS & Geospatial
    "EnterpriseGISEngine",
    "SpatialAnalyticsEngine",
    "RealTimeTracker",

    # Collaboration
    "WorkspaceManager",
    "VisualizationVersionControl",

    # Data Integration
    "EnterpriseDataConnectors",

    # AI & Analytics
    "VizlyAI",
    "ChartRecommendationEngine",
]

__version__ = "1.0.0-enterprise"
__enterprise_license__ = "Commercial - Enterprise License Required"
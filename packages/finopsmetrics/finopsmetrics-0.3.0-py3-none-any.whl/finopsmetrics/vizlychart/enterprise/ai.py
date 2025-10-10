"""
Enterprise AI Features
======================

AI-powered features for Vizly Enterprise including smart chart recommendations,
automated insights, and intelligent data analysis.

Features:
- Chart type recommendation based on data
- Automated insight generation
- Smart color palette selection
- Data quality assessment
- Anomaly detection in visualizations
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import statistics

logger = logging.getLogger(__name__)


class ChartType(Enum):
    """Supported chart types."""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    BOX = "box"
    AREA = "area"
    BUBBLE = "bubble"
    TREEMAP = "treemap"


class DataType(Enum):
    """Data column types."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    TEMPORAL = "temporal"
    TEXT = "text"
    BOOLEAN = "boolean"


@dataclass
class ChartRecommendation:
    """AI-generated chart recommendation."""
    chart_type: ChartType
    confidence: float
    reasoning: str
    suggested_x_axis: Optional[str] = None
    suggested_y_axis: Optional[str] = None
    suggested_color: Optional[str] = None
    additional_options: Dict[str, Any] = None


@dataclass
class DataInsight:
    """Automated data insight."""
    insight_type: str
    title: str
    description: str
    confidence: float
    affected_columns: List[str]
    visualization_suggestion: Optional[ChartType] = None


class ChartRecommendationEngine:
    """
    AI-powered chart recommendation engine.

    Analyzes data characteristics and recommends optimal chart types
    with confidence scores and reasoning.

    Features:
    - Automatic data type detection
    - Chart type recommendation
    - Axis and color mapping suggestions
    - Best practices enforcement
    - Multi-chart recommendations
    """

    def __init__(self):
        """Initialize recommendation engine."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Chart recommendation engine initialized")

    def analyze_data(self, data: List[Dict[str, Any]]) -> Dict[str, DataType]:
        """
        Analyze data and detect column types.

        Args:
            data: List of data points

        Returns:
            Dictionary mapping column names to detected types
        """
        if not data:
            return {}

        column_types = {}
        first_row = data[0]

        for column in first_row.keys():
            values = [row.get(column) for row in data if row.get(column) is not None]

            if not values:
                column_types[column] = DataType.TEXT
                continue

            # Check if numeric
            if all(isinstance(v, (int, float)) for v in values):
                column_types[column] = DataType.NUMERIC

            # Check if temporal (simple heuristic)
            elif all(isinstance(v, str) and any(sep in v for sep in ['-', '/', ':']) for v in values[:5]):
                column_types[column] = DataType.TEMPORAL

            # Check if boolean
            elif all(isinstance(v, bool) or v in [True, False, 0, 1, 'true', 'false'] for v in values):
                column_types[column] = DataType.BOOLEAN

            # Check if categorical (limited unique values)
            elif len(set(values)) <= max(10, len(values) * 0.1):
                column_types[column] = DataType.CATEGORICAL

            else:
                column_types[column] = DataType.TEXT

        self.logger.debug(f"Detected column types: {column_types}")
        return column_types

    def recommend_chart(
        self, data: List[Dict[str, Any]], goal: Optional[str] = None
    ) -> List[ChartRecommendation]:
        """
        Recommend chart types for data.

        Args:
            data: Data to visualize
            goal: Optional visualization goal
                  ('trend', 'comparison', 'distribution', 'relationship', 'composition')

        Returns:
            List of chart recommendations ranked by confidence
        """
        if not data:
            return []

        column_types = self.analyze_data(data)
        numeric_cols = [c for c, t in column_types.items() if t == DataType.NUMERIC]
        categorical_cols = [c for c, t in column_types.items() if t == DataType.CATEGORICAL]
        temporal_cols = [c for c, t in column_types.items() if t == DataType.TEMPORAL]

        recommendations = []

        # Time series data
        if temporal_cols and numeric_cols:
            recommendations.append(
                ChartRecommendation(
                    chart_type=ChartType.LINE,
                    confidence=0.95,
                    reasoning="Temporal data with numeric values - ideal for line chart",
                    suggested_x_axis=temporal_cols[0],
                    suggested_y_axis=numeric_cols[0],
                )
            )

            recommendations.append(
                ChartRecommendation(
                    chart_type=ChartType.AREA,
                    confidence=0.85,
                    reasoning="Temporal trends can also be shown as area chart",
                    suggested_x_axis=temporal_cols[0],
                    suggested_y_axis=numeric_cols[0],
                )
            )

        # Categorical vs numeric
        if categorical_cols and numeric_cols:
            # Small number of categories -> bar chart
            if len(categorical_cols) > 0:
                cat_col = categorical_cols[0]
                unique_values = len(set(row.get(cat_col) for row in data))

                if unique_values <= 10:
                    recommendations.append(
                        ChartRecommendation(
                            chart_type=ChartType.BAR,
                            confidence=0.90,
                            reasoning=f"Comparing {unique_values} categories - bar chart is clearest",
                            suggested_x_axis=cat_col,
                            suggested_y_axis=numeric_cols[0],
                        )
                    )

                # Composition/parts of whole
                if goal == "composition":
                    recommendations.append(
                        ChartRecommendation(
                            chart_type=ChartType.PIE,
                            confidence=0.80,
                            reasoning="Showing composition of categories",
                            suggested_color=cat_col,
                        )
                    )

        # Multiple numeric columns - scatter plot for relationship
        if len(numeric_cols) >= 2:
            recommendations.append(
                ChartRecommendation(
                    chart_type=ChartType.SCATTER,
                    confidence=0.85,
                    reasoning="Two numeric variables - scatter plot shows relationship",
                    suggested_x_axis=numeric_cols[0],
                    suggested_y_axis=numeric_cols[1],
                    suggested_color=categorical_cols[0] if categorical_cols else None,
                )
            )

        # Single numeric column - distribution
        if len(numeric_cols) == 1 and not categorical_cols and not temporal_cols:
            recommendations.append(
                ChartRecommendation(
                    chart_type=ChartType.HISTOGRAM,
                    confidence=0.90,
                    reasoning="Single numeric variable - histogram shows distribution",
                    suggested_x_axis=numeric_cols[0],
                )
            )

            recommendations.append(
                ChartRecommendation(
                    chart_type=ChartType.BOX,
                    confidence=0.80,
                    reasoning="Box plot shows distribution with quartiles and outliers",
                    suggested_y_axis=numeric_cols[0],
                )
            )

        # Sort by confidence
        recommendations.sort(key=lambda r: r.confidence, reverse=True)

        self.logger.info(f"Generated {len(recommendations)} chart recommendations")
        return recommendations

    def suggest_colors(
        self, data: List[Dict[str, Any]], column: str
    ) -> Dict[str, str]:
        """
        Suggest color mapping for categorical data.

        Args:
            data: Data
            column: Column to create color mapping for

        Returns:
            Dictionary mapping values to colors
        """
        values = list(set(row.get(column) for row in data if row.get(column) is not None))

        # Predefined color palettes
        categorical_palette = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
            "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
        ]

        color_mapping = {}
        for i, value in enumerate(values):
            color_mapping[value] = categorical_palette[i % len(categorical_palette)]

        return color_mapping


class VizlyAI:
    """
    AI-powered visualization assistant.

    Provides intelligent features including:
    - Automated insight generation
    - Data quality assessment
    - Anomaly detection
    - Natural language chart generation
    - Smart defaults and suggestions
    """

    def __init__(self):
        """Initialize Vizly AI."""
        self.recommendation_engine = ChartRecommendationEngine()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Vizly AI initialized")

    def generate_insights(self, data: List[Dict[str, Any]]) -> List[DataInsight]:
        """
        Generate automated insights from data.

        Args:
            data: Data to analyze

        Returns:
            List of insights
        """
        if not data:
            return []

        insights = []
        column_types = self.recommendation_engine.analyze_data(data)

        # Analyze numeric columns
        numeric_cols = [c for c, t in column_types.items() if t == DataType.NUMERIC]

        for col in numeric_cols:
            values = [row[col] for row in data if col in row and isinstance(row[col], (int, float))]

            if not values:
                continue

            mean_val = statistics.mean(values)
            if len(values) >= 2:
                stdev_val = statistics.stdev(values)

                # Check for high variance
                if stdev_val / mean_val > 1.0 if mean_val != 0 else False:
                    insights.append(
                        DataInsight(
                            insight_type="high_variance",
                            title=f"High Variance in {col}",
                            description=f"{col} shows high variability (CV={stdev_val/mean_val:.2f})",
                            confidence=0.85,
                            affected_columns=[col],
                            visualization_suggestion=ChartType.BOX,
                        )
                    )

                # Check for outliers (simple IQR method)
                sorted_vals = sorted(values)
                q1_idx = len(sorted_vals) // 4
                q3_idx = (3 * len(sorted_vals)) // 4
                q1 = sorted_vals[q1_idx]
                q3 = sorted_vals[q3_idx]
                iqr = q3 - q1

                if iqr > 0:
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    outliers = [v for v in values if v < lower_bound or v > upper_bound]

                    if len(outliers) > 0:
                        insights.append(
                            DataInsight(
                                insight_type="outliers",
                                title=f"Outliers Detected in {col}",
                                description=f"Found {len(outliers)} outliers ({len(outliers)/len(values)*100:.1f}%)",
                                confidence=0.90,
                                affected_columns=[col],
                                visualization_suggestion=ChartType.BOX,
                            )
                        )

            # Check for trends (if temporal data exists)
            temporal_cols = [c for c, t in column_types.items() if t == DataType.TEMPORAL]
            if temporal_cols:
                # Simple trend detection: check if generally increasing or decreasing
                if len(values) >= 5:
                    first_half_avg = statistics.mean(values[:len(values)//2])
                    second_half_avg = statistics.mean(values[len(values)//2:])

                    if second_half_avg > first_half_avg * 1.2:
                        insights.append(
                            DataInsight(
                                insight_type="upward_trend",
                                title=f"Upward Trend in {col}",
                                description=f"{col} shows upward trend (20%+ increase)",
                                confidence=0.75,
                                affected_columns=[col, temporal_cols[0]],
                                visualization_suggestion=ChartType.LINE,
                            )
                        )
                    elif second_half_avg < first_half_avg * 0.8:
                        insights.append(
                            DataInsight(
                                insight_type="downward_trend",
                                title=f"Downward Trend in {col}",
                                description=f"{col} shows downward trend (20%+ decrease)",
                                confidence=0.75,
                                affected_columns=[col, temporal_cols[0]],
                                visualization_suggestion=ChartType.LINE,
                            )
                        )

        self.logger.info(f"Generated {len(insights)} insights")
        return insights

    def assess_data_quality(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess data quality.

        Args:
            data: Data to assess

        Returns:
            Quality assessment report
        """
        if not data:
            return {"quality_score": 0, "issues": ["No data provided"]}

        total_cells = 0
        missing_cells = 0
        columns = set()
        issues = []

        for row in data:
            columns.update(row.keys())
            total_cells += len(columns)
            missing_cells += sum(1 for v in row.values() if v is None or v == "")

        # Completeness score
        completeness = 1.0 - (missing_cells / total_cells) if total_cells > 0 else 0

        if completeness < 0.9:
            issues.append(f"Data is {completeness*100:.1f}% complete ({missing_cells} missing values)")

        # Consistency check (all rows have same columns)
        column_counts = {}
        for row in data:
            col_count = len(row.keys())
            column_counts[col_count] = column_counts.get(col_count, 0) + 1

        if len(column_counts) > 1:
            issues.append("Inconsistent column counts across rows")

        # Overall quality score
        quality_score = completeness * 100

        return {
            "quality_score": round(quality_score, 2),
            "completeness": round(completeness * 100, 2),
            "total_rows": len(data),
            "total_columns": len(columns),
            "missing_values": missing_cells,
            "issues": issues,
            "recommendation": "Good data quality" if quality_score >= 90 else "Consider cleaning data"
        }

    def recommend_chart(
        self, data: List[Dict[str, Any]], goal: Optional[str] = None
    ) -> List[ChartRecommendation]:
        """
        Recommend chart type using AI.

        Delegates to ChartRecommendationEngine.
        """
        return self.recommendation_engine.recommend_chart(data, goal)

    def get_smart_defaults(
        self, data: List[Dict[str, Any]], chart_type: ChartType
    ) -> Dict[str, Any]:
        """
        Get smart default configuration for a chart.

        Args:
            data: Data to visualize
            chart_type: Chart type

        Returns:
            Dictionary of smart defaults
        """
        column_types = self.recommendation_engine.analyze_data(data)
        numeric_cols = [c for c, t in column_types.items() if t == DataType.NUMERIC]
        categorical_cols = [c for c, t in column_types.items() if t == DataType.CATEGORICAL]
        temporal_cols = [c for c, t in column_types.items() if t == DataType.TEMPORAL]

        defaults = {
            "title": f"{chart_type.value.title()} Chart",
            "show_legend": len(categorical_cols) > 0,
            "show_grid": True,
        }

        # Chart-specific defaults
        if chart_type == ChartType.LINE:
            defaults.update({
                "x_axis": temporal_cols[0] if temporal_cols else (numeric_cols[0] if numeric_cols else None),
                "y_axis": numeric_cols[0] if numeric_cols else None,
                "line_style": "solid",
                "marker_size": 5,
            })

        elif chart_type == ChartType.BAR:
            defaults.update({
                "x_axis": categorical_cols[0] if categorical_cols else None,
                "y_axis": numeric_cols[0] if numeric_cols else None,
                "orientation": "vertical",
            })

        elif chart_type == ChartType.SCATTER:
            defaults.update({
                "x_axis": numeric_cols[0] if len(numeric_cols) > 0 else None,
                "y_axis": numeric_cols[1] if len(numeric_cols) > 1 else None,
                "color_by": categorical_cols[0] if categorical_cols else None,
                "marker_size": 50,
            })

        return defaults

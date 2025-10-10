"""
Unit tests for VizlyChart Enterprise Features.

Tests for:
- WorkspaceManager
- VisualizationVersionControl
- VizlyAI
- ChartRecommendationEngine
"""

import pytest
import time
from datetime import datetime
from finopsmetrics.vizlychart.enterprise import (
    WorkspaceManager,
    VisualizationVersionControl,
    VizlyAI,
    ChartRecommendationEngine,
)
from finopsmetrics.vizlychart.enterprise.collaboration import (
    WorkspaceRole,
    WorkspaceVisibility,
)
from finopsmetrics.vizlychart.enterprise.ai import (
    ChartType,
    DataType,
)


@pytest.mark.unit
class TestWorkspaceManager:
    """Test suite for WorkspaceManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = WorkspaceManager()
        self.owner_id = "user_001"
        self.member_id = "user_002"

    def test_initialization(self):
        """Test WorkspaceManager initialization."""
        assert self.manager is not None
        assert hasattr(self.manager, 'create_workspace')
        assert hasattr(self.manager, 'add_member')

    def test_create_workspace(self):
        """Test workspace creation."""
        workspace_id = self.manager.create_workspace(
            name="Test Workspace",
            description="A test workspace",
            owner_id=self.owner_id,
            owner_username="owner",
            owner_email="owner@test.com"
        )

        assert workspace_id is not None
        assert len(workspace_id) > 0

        # Verify workspace exists
        workspace = self.manager.get_workspace(workspace_id)
        assert workspace is not None
        assert workspace.name == "Test Workspace"
        assert workspace.owner_id == self.owner_id

    def test_workspace_visibility(self):
        """Test workspace visibility settings."""
        # Create private workspace
        private_ws = self.manager.create_workspace(
            name="Private Workspace",
            description="Private workspace",
            owner_id=self.owner_id,
            owner_username="owner",
            owner_email="owner@test.com",
            visibility=WorkspaceVisibility.PRIVATE
        )

        workspace = self.manager.get_workspace(private_ws)
        assert workspace.visibility == WorkspaceVisibility.PRIVATE

        # Create public workspace
        public_ws = self.manager.create_workspace(
            name="Public Workspace",
            description="Public workspace",
            owner_id=self.owner_id,
            owner_username="owner",
            owner_email="owner@test.com",
            visibility=WorkspaceVisibility.PUBLIC
        )

        workspace = self.manager.get_workspace(public_ws)
        assert workspace.visibility == WorkspaceVisibility.PUBLIC

    def test_add_member(self):
        """Test adding members to workspace."""
        workspace_id = self.manager.create_workspace(
            name="Team Workspace",
            description="Team workspace",
            owner_id=self.owner_id,
            owner_username="owner",
            owner_email="owner@test.com"
        )

        # Add member as editor
        result = self.manager.add_member(
            workspace_id=workspace_id,
            user_id=self.member_id,
            username="member",
            email="member@test.com",
            role=WorkspaceRole.EDITOR
        )

        assert result is True

        # Verify member access
        has_access = self.manager.has_access(
            workspace_id=workspace_id,
            user_id=self.member_id,
            required_role=WorkspaceRole.VIEWER
        )
        assert has_access is True

    def test_remove_member(self):
        """Test removing members from workspace."""
        workspace_id = self.manager.create_workspace(
            name="Test Workspace",
            description="Test",
            owner_id=self.owner_id,
            owner_username="owner",
            owner_email="owner@test.com"
        )

        # Add and then remove member
        self.manager.add_member(
            workspace_id, self.member_id, "member", "member@test.com", WorkspaceRole.EDITOR
        )
        result = self.manager.remove_member(workspace_id, self.member_id)

        assert result is True

        # Verify member no longer has access
        has_access = self.manager.has_access(
            workspace_id=workspace_id,
            user_id=self.member_id,
            required_role=WorkspaceRole.VIEWER
        )
        assert has_access is False

    def test_update_member_role(self):
        """Test updating member role."""
        workspace_id = self.manager.create_workspace(
            name="Test Workspace",
            description="Test",
            owner_id=self.owner_id,
            owner_username="owner",
            owner_email="owner@test.com"
        )

        # Add member as viewer
        self.manager.add_member(
            workspace_id, self.member_id, "member", "member@test.com", WorkspaceRole.VIEWER
        )

        # Upgrade to editor
        result = self.manager.update_member_role(
            workspace_id=workspace_id,
            user_id=self.member_id,
            new_role=WorkspaceRole.EDITOR
        )

        assert result is True

        # Verify new role
        has_edit = self.manager.has_access(
            workspace_id=workspace_id,
            user_id=self.member_id,
            required_role=WorkspaceRole.EDITOR
        )
        assert has_edit is True

    def test_role_hierarchy(self):
        """Test role hierarchy and permissions."""
        workspace_id = self.manager.create_workspace(
            name="Test Workspace",
            description="Test",
            owner_id=self.owner_id,
            owner_username="owner",
            owner_email="owner@test.com"
        )

        # Add member as viewer
        self.manager.add_member(
            workspace_id, self.member_id, "member", "member@test.com", WorkspaceRole.VIEWER
        )

        # Viewer should have viewer access
        assert self.manager.has_access(workspace_id, self.member_id, WorkspaceRole.VIEWER)

        # But not editor access
        assert not self.manager.has_access(workspace_id, self.member_id, WorkspaceRole.EDITOR)

        # Owner should have all access
        assert self.manager.has_access(workspace_id, self.owner_id, WorkspaceRole.OWNER)
        assert self.manager.has_access(workspace_id, self.owner_id, WorkspaceRole.ADMIN)
        assert self.manager.has_access(workspace_id, self.owner_id, WorkspaceRole.EDITOR)

    def test_list_workspaces(self):
        """Test listing workspaces for a user."""
        # Create multiple workspaces
        ws1 = self.manager.create_workspace(
            "WS1", "Test 1", self.owner_id, "owner", "owner@test.com"
        )
        ws2 = self.manager.create_workspace(
            "WS2", "Test 2", self.owner_id, "owner", "owner@test.com"
        )

        workspaces = self.manager.list_user_workspaces(self.owner_id)

        assert len(workspaces) >= 2
        workspace_ids = [ws.workspace_id for ws in workspaces]
        assert ws1 in workspace_ids
        assert ws2 in workspace_ids


@pytest.mark.unit
class TestVisualizationVersionControl:
    """Test suite for VisualizationVersionControl."""

    def setup_method(self):
        """Set up test fixtures."""
        self.vcs = VisualizationVersionControl()
        self.chart_id = "chart_001"
        self.user_id = "user_001"

    def test_initialization(self):
        """Test VisualizationVersionControl initialization."""
        assert self.vcs is not None
        assert hasattr(self.vcs, 'commit')
        assert hasattr(self.vcs, 'rollback')

    def test_commit_version(self):
        """Test committing a chart version."""
        chart_data = {
            "type": "line",
            "data": [1, 2, 3, 4, 5],
            "labels": ["A", "B", "C", "D", "E"]
        }

        version_id = self.vcs.commit(
            chart_id=self.chart_id,
            chart_data=chart_data,
            user_id=self.user_id,
            message="Initial commit"
        )

        assert version_id is not None
        assert len(version_id) > 0

    def test_commit_history(self):
        """Test commit history tracking."""
        # Create multiple commits
        for i in range(3):
            chart_data = {"data": [i] * 5}
            self.vcs.commit(
                chart_id=self.chart_id,
                chart_data=chart_data,
                user_id=self.user_id,
                message=f"Commit {i+1}"
            )

        # Get history
        history = self.vcs.get_history(self.chart_id)

        assert len(history) == 3
        assert history[0].commit_message == "Commit 1"  # Oldest first
        assert history[2].commit_message == "Commit 3"

    def test_rollback_version(self):
        """Test rolling back to previous version."""
        # Create initial version
        v1_data = {"data": [1, 2, 3]}
        v1 = self.vcs.commit(self.chart_id, v1_data, self.user_id, "Version 1")

        # Create second version
        v2_data = {"data": [4, 5, 6]}
        v2 = self.vcs.commit(self.chart_id, v2_data, self.user_id, "Version 2")

        # Rollback to v1
        rollback_id = self.vcs.rollback(self.chart_id, v1, self.user_id)

        assert rollback_id is not None

        # Get latest version
        latest = self.vcs.get_version(self.chart_id, rollback_id)
        assert latest.chart_data == v1_data

    def test_tag_version(self):
        """Test tagging versions."""
        # Create a version
        chart_data = {"data": [1, 2, 3]}
        version_id = self.vcs.commit(self.chart_id, chart_data, self.user_id, "Release candidate")

        # Tag it
        result = self.vcs.tag_version(self.chart_id, version_id, "v1.0")

        assert result is True

        # Verify tag exists
        version = self.vcs.get_version(self.chart_id, version_id)
        assert "v1.0" in version.tags

    def test_compare_versions(self):
        """Test comparing two versions."""
        # Create two versions
        v1_data = {"type": "line", "data": [1, 2, 3]}
        v1 = self.vcs.commit(self.chart_id, v1_data, self.user_id, "V1")

        v2_data = {"type": "bar", "data": [4, 5, 6]}
        v2 = self.vcs.commit(self.chart_id, v2_data, self.user_id, "V2")

        # Compare
        diff = self.vcs.compare_versions(self.chart_id, v1, v2)

        assert diff is not None
        assert len(diff) > 0

    def test_get_latest_version(self):
        """Test getting latest version."""
        # Create multiple versions
        for i in range(3):
            self.vcs.commit(
                self.chart_id,
                {"data": [i]},
                self.user_id,
                f"Version {i+1}"
            )

        # Get latest
        latest = self.vcs.get_latest_version(self.chart_id)

        assert latest is not None
        assert latest.commit_message == "Version 3"



@pytest.mark.unit
class TestChartRecommendationEngine:
    """Test suite for ChartRecommendationEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ChartRecommendationEngine()

    def test_initialization(self):
        """Test ChartRecommendationEngine initialization."""
        assert self.engine is not None
        assert hasattr(self.engine, 'analyze_data')
        assert hasattr(self.engine, 'recommend_chart')

    def test_analyze_data_numeric(self):
        """Test data analysis with numeric columns."""
        data = [
            {"value": 10, "category": "A"},
            {"value": 20, "category": "B"},
            {"value": 30, "category": "C"}
        ]

        column_types = self.engine.analyze_data(data)

        assert column_types["value"] == DataType.NUMERIC
        assert column_types["category"] == DataType.CATEGORICAL

    def test_analyze_data_temporal(self):
        """Test data analysis with temporal columns."""
        data = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 150},
            {"date": "2024-01-03", "value": 200}
        ]

        column_types = self.engine.analyze_data(data)

        assert column_types["date"] == DataType.TEMPORAL
        assert column_types["value"] == DataType.NUMERIC

    def test_recommend_chart_timeseries(self):
        """Test chart recommendation for time series data."""
        data = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 150},
            {"date": "2024-01-03", "value": 200}
        ]

        recommendations = self.engine.recommend_chart(data)

        assert len(recommendations) > 0
        # First recommendation should be line chart for time series
        assert recommendations[0].chart_type == ChartType.LINE
        assert recommendations[0].confidence > 0.8

    def test_recommend_chart_categorical(self):
        """Test chart recommendation for categorical data."""
        data = [
            {"category": "A", "value": 10},
            {"category": "B", "value": 20},
            {"category": "C", "value": 15}
        ]

        recommendations = self.engine.recommend_chart(data)

        assert len(recommendations) > 0
        # Should recommend bar chart for categorical data
        bar_recs = [r for r in recommendations if r.chart_type == ChartType.BAR]
        assert len(bar_recs) > 0
        assert bar_recs[0].confidence > 0.8

    def test_recommend_chart_scatter(self):
        """Test chart recommendation for two numeric variables."""
        data = [
            {"x": 1, "y": 2},
            {"x": 2, "y": 4},
            {"x": 3, "y": 6}
        ]

        recommendations = self.engine.recommend_chart(data)

        # Should include scatter plot for two numeric variables
        scatter_recs = [r for r in recommendations if r.chart_type == ChartType.SCATTER]
        assert len(scatter_recs) > 0

    def test_recommend_chart_distribution(self):
        """Test chart recommendation for single numeric variable."""
        data = [{"value": i} for i in range(100)]

        recommendations = self.engine.recommend_chart(data)

        # Should recommend histogram for distribution
        histogram_recs = [r for r in recommendations if r.chart_type == ChartType.HISTOGRAM]
        assert len(histogram_recs) > 0

    def test_recommend_with_goal(self):
        """Test chart recommendation with specific goal."""
        data = [
            {"category": "A", "value": 25},
            {"category": "B", "value": 35},
            {"category": "C", "value": 40}
        ]

        recommendations = self.engine.recommend_chart(data, goal="composition")

        # Should include pie chart for composition goal
        pie_recs = [r for r in recommendations if r.chart_type == ChartType.PIE]
        assert len(pie_recs) > 0

    def test_suggest_colors(self):
        """Test color suggestion for categorical data."""
        data = [
            {"category": "A", "value": 10},
            {"category": "B", "value": 20},
            {"category": "C", "value": 15}
        ]

        color_mapping = self.engine.suggest_colors(data, "category")

        assert len(color_mapping) == 3
        assert "A" in color_mapping
        assert "B" in color_mapping
        assert "C" in color_mapping
        # Colors should be hex codes
        for color in color_mapping.values():
            assert color.startswith("#")

    def test_empty_data(self):
        """Test handling empty data."""
        recommendations = self.engine.recommend_chart([])
        assert len(recommendations) == 0


@pytest.mark.unit
class TestVizlyAI:
    """Test suite for VizlyAI."""

    def setup_method(self):
        """Set up test fixtures."""
        self.ai = VizlyAI()

    def test_initialization(self):
        """Test VizlyAI initialization."""
        assert self.ai is not None
        assert hasattr(self.ai, 'generate_insights')
        assert hasattr(self.ai, 'assess_data_quality')

    def test_generate_insights_outliers(self):
        """Test insight generation for outliers."""
        # Data with outliers
        data = [{"value": i} for i in range(100)]
        data.append({"value": 1000})  # Outlier

        insights = self.ai.generate_insights(data)

        # Should detect outliers
        outlier_insights = [i for i in insights if i.insight_type == "outliers"]
        assert len(outlier_insights) > 0

    def test_generate_insights_variance(self):
        """Test insight generation for high variance."""
        # Data with high variance
        data = [
            {"value": 10},
            {"value": 100},
            {"value": 15},
            {"value": 200},
            {"value": 5}
        ]

        insights = self.ai.generate_insights(data)

        # Should detect high variance
        variance_insights = [i for i in insights if i.insight_type == "high_variance"]
        assert len(variance_insights) > 0

    def test_generate_insights_trend(self):
        """Test insight generation for trends."""
        # Data with upward trend
        data = [
            {"date": f"2024-01-{i:02d}", "value": i * 10}
            for i in range(1, 11)
        ]

        insights = self.ai.generate_insights(data)

        # Should detect upward trend
        trend_insights = [i for i in insights if "trend" in i.insight_type]
        assert len(trend_insights) > 0

    def test_assess_data_quality_complete(self):
        """Test data quality assessment for complete data."""
        data = [
            {"a": 1, "b": 2, "c": 3},
            {"a": 4, "b": 5, "c": 6},
            {"a": 7, "b": 8, "c": 9}
        ]

        assessment = self.ai.assess_data_quality(data)

        assert assessment["quality_score"] >= 90
        assert assessment["completeness"] >= 90
        assert assessment["total_rows"] == 3
        assert assessment["total_columns"] == 3
        assert assessment["missing_values"] == 0

    def test_assess_data_quality_incomplete(self):
        """Test data quality assessment for incomplete data."""
        data = [
            {"a": 1, "b": 2, "c": None},
            {"a": 4, "b": None, "c": 6},
            {"a": None, "b": 8, "c": 9}
        ]

        assessment = self.ai.assess_data_quality(data)

        assert assessment["quality_score"] < 100
        assert assessment["missing_values"] > 0
        assert len(assessment["issues"]) > 0

    def test_assess_data_quality_empty(self):
        """Test data quality assessment for empty data."""
        assessment = self.ai.assess_data_quality([])

        assert assessment["quality_score"] == 0
        assert "No data provided" in assessment["issues"]

    def test_recommend_chart_delegation(self):
        """Test that VizlyAI delegates to ChartRecommendationEngine."""
        data = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 150}
        ]

        recommendations = self.ai.recommend_chart(data)

        assert len(recommendations) > 0
        assert recommendations[0].chart_type is not None

    def test_get_smart_defaults_line(self):
        """Test smart defaults for line chart."""
        data = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 150}
        ]

        defaults = self.ai.get_smart_defaults(data, ChartType.LINE)

        assert "title" in defaults
        assert "x_axis" in defaults
        assert "y_axis" in defaults
        assert defaults["show_grid"] is True

    def test_get_smart_defaults_bar(self):
        """Test smart defaults for bar chart."""
        data = [
            {"category": "A", "value": 10},
            {"category": "B", "value": 20}
        ]

        defaults = self.ai.get_smart_defaults(data, ChartType.BAR)

        assert "title" in defaults
        assert "x_axis" in defaults
        assert "y_axis" in defaults
        assert "orientation" in defaults

    def test_get_smart_defaults_scatter(self):
        """Test smart defaults for scatter chart."""
        data = [
            {"x": 1, "y": 2, "category": "A"},
            {"x": 3, "y": 4, "category": "B"}
        ]

        defaults = self.ai.get_smart_defaults(data, ChartType.SCATTER)

        assert "x_axis" in defaults
        assert "y_axis" in defaults
        assert "color_by" in defaults
        assert defaults["marker_size"] > 0


@pytest.mark.integration
class TestEnterpriseIntegration:
    """Integration tests for enterprise features."""

    def test_workspace_with_version_control(self):
        """Test workspace management integrated with version control."""
        # Create workspace
        wm = WorkspaceManager()
        workspace_id = wm.create_workspace(
            name="VCS Test Workspace",
            description="Testing version control",
            owner_id="user_001",
            owner_username="testuser",
            owner_email="test@example.com"
        )

        # Create chart with version control
        vcs = VisualizationVersionControl()
        chart_id = "chart_in_workspace"
        chart_data = {"type": "line", "data": [1, 2, 3]}

        version_id = vcs.commit(
            chart_id=chart_id,
            chart_data=chart_data,
            user_id="user_001",
            message="Initial chart in workspace"
        )

        # Verify both components work together
        assert workspace_id is not None
        assert version_id is not None

    def test_ai_recommendations_workflow(self):
        """Test complete AI-powered workflow."""
        ai = VizlyAI()

        # Sample data
        data = [
            {"date": "2024-01-01", "sales": 100, "region": "North"},
            {"date": "2024-01-02", "sales": 150, "region": "North"},
            {"date": "2024-01-03", "sales": 200, "region": "South"},
            {"date": "2024-01-04", "sales": 175, "region": "South"}
        ]

        # Step 1: Assess data quality
        quality = ai.assess_data_quality(data)
        assert quality["quality_score"] > 0

        # Step 2: Generate insights
        insights = ai.generate_insights(data)
        assert isinstance(insights, list)

        # Step 3: Get chart recommendations
        recommendations = ai.recommend_chart(data)
        assert len(recommendations) > 0

        # Step 4: Get smart defaults for top recommendation
        top_chart = recommendations[0]
        defaults = ai.get_smart_defaults(data, top_chart.chart_type)
        assert "title" in defaults

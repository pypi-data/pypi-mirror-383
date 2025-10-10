"""
Tests for SaaS Telemetry Agent
================================

Test the new SaaS service collectors (Kafka, Vercel, Docker Hub, Elasticsearch).
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import sys
import os
import json
import tempfile
import pytest

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'agents'))

from saas_services_telemetry_agent import (
    ConfluentKafkaCollector,
    VercelCollector,
    DockerHubCollector,
    ElasticsearchCollector,
    SaaSServicesTelemetryAgent
)


class TestConfluentKafkaCollector:
    """Test Confluent Kafka collector."""

    def test_initialization(self):
        """Test collector initialization."""
        collector = ConfluentKafkaCollector(
            api_key="test_key",
            api_secret="test_secret"
        )
        assert collector.api_key == "test_key"
        assert collector.api_secret == "test_secret"
        assert collector.base_url == "https://api.confluent.cloud"

    def test_pricing_tiers(self):
        """Test pricing tier definitions."""
        collector = ConfluentKafkaCollector("key", "secret")
        assert "basic" in collector.CLUSTER_PRICING
        assert "standard" in collector.CLUSTER_PRICING
        assert "dedicated" in collector.CLUSTER_PRICING
        assert collector.CLUSTER_PRICING["basic"] == 0.11
        assert collector.CLUSTER_PRICING["standard"] == 0.45
        assert collector.CLUSTER_PRICING["dedicated"] == 1.50


class TestVercelCollector:
    """Test Vercel collector."""

    def test_initialization(self):
        """Test collector initialization."""
        collector = VercelCollector(token="test_token")
        assert collector.token == "test_token"
        assert collector.base_url == "https://api.vercel.com"
        assert collector.team_id is None

    def test_initialization_with_team(self):
        """Test collector initialization with team ID."""
        collector = VercelCollector(token="test_token", team_id="team_123")
        assert collector.token == "test_token"
        assert collector.team_id == "team_123"


class TestDockerHubCollector:
    """Test Docker Hub collector."""

    def test_initialization(self):
        """Test collector initialization."""
        collector = DockerHubCollector(
            username="testuser",
            password="testpass"
        )
        assert collector.username == "testuser"
        assert collector.password == "testpass"
        assert collector.organization == "testuser"
        assert collector.base_url == "https://hub.docker.com/v2"

    def test_initialization_with_org(self):
        """Test collector initialization with organization."""
        collector = DockerHubCollector(
            username="testuser",
            password="testpass",
            organization="testorg"
        )
        assert collector.username == "testuser"
        assert collector.organization == "testorg"


class TestElasticsearchCollector:
    """Test Elasticsearch collector."""

    def test_initialization(self):
        """Test collector initialization."""
        collector = ElasticsearchCollector(
            cloud_id="test_cloud_id",
            api_key="test_api_key"
        )
        assert collector.cloud_id == "test_cloud_id"
        assert collector.api_key == "test_api_key"
        assert collector.base_url == "https://api.elastic-cloud.com/api/v1"


class TestSaaSServicesTelemetryAgent:
    """Test SaaS services telemetry agent."""

    def test_initialization_with_empty_config(self):
        """Test agent initialization with empty config."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            config_file = f.name

        try:
            agent = SaaSServicesTelemetryAgent(
                finopsmetrics_endpoint="http://localhost:8080",
                config_file=config_file
            )
            assert agent.finopsmetrics_endpoint == "http://localhost:8080"
            assert len(agent.collectors) == 0
        finally:
            os.unlink(config_file)

    def test_initialization_with_kafka_enabled(self):
        """Test agent initialization with Kafka enabled."""
        config = {
            "confluent_kafka": {
                "enabled": True,
                "api_key": "test_key",
                "api_secret": "test_secret"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            agent = SaaSServicesTelemetryAgent(
                finopsmetrics_endpoint="http://localhost:8080",
                config_file=config_file
            )
            assert len(agent.collectors) == 1
            assert agent.collectors[0][0] == "confluent_kafka"
        finally:
            os.unlink(config_file)

    def test_initialization_with_vercel_enabled(self):
        """Test agent initialization with Vercel enabled."""
        config = {
            "vercel": {
                "enabled": True,
                "token": "test_token"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            agent = SaaSServicesTelemetryAgent(
                finopsmetrics_endpoint="http://localhost:8080",
                config_file=config_file
            )
            assert len(agent.collectors) == 1
            assert agent.collectors[0][0] == "vercel"
        finally:
            os.unlink(config_file)

    def test_initialization_with_docker_hub_enabled(self):
        """Test agent initialization with Docker Hub enabled."""
        config = {
            "docker_hub": {
                "enabled": True,
                "username": "testuser",
                "password": "testpass"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            agent = SaaSServicesTelemetryAgent(
                finopsmetrics_endpoint="http://localhost:8080",
                config_file=config_file
            )
            assert len(agent.collectors) == 1
            assert agent.collectors[0][0] == "docker_hub"
        finally:
            os.unlink(config_file)

    def test_initialization_with_elasticsearch_enabled(self):
        """Test agent initialization with Elasticsearch enabled."""
        config = {
            "elasticsearch": {
                "enabled": True,
                "cloud_id": "test_cloud_id",
                "api_key": "test_api_key"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            agent = SaaSServicesTelemetryAgent(
                finopsmetrics_endpoint="http://localhost:8080",
                config_file=config_file
            )
            assert len(agent.collectors) == 1
            assert agent.collectors[0][0] == "elasticsearch"
        finally:
            os.unlink(config_file)

    def test_initialization_with_all_new_services(self):
        """Test agent initialization with all new services enabled."""
        config = {
            "confluent_kafka": {
                "enabled": True,
                "api_key": "test_key",
                "api_secret": "test_secret"
            },
            "vercel": {
                "enabled": True,
                "token": "test_token"
            },
            "docker_hub": {
                "enabled": True,
                "username": "testuser",
                "password": "testpass"
            },
            "elasticsearch": {
                "enabled": True,
                "cloud_id": "test_cloud_id",
                "api_key": "test_api_key"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            agent = SaaSServicesTelemetryAgent(
                finopsmetrics_endpoint="http://localhost:8080",
                config_file=config_file
            )
            assert len(agent.collectors) == 4
            collector_names = [name for name, _ in agent.collectors]
            assert "confluent_kafka" in collector_names
            assert "vercel" in collector_names
            assert "docker_hub" in collector_names
            assert "elasticsearch" in collector_names
        finally:
            os.unlink(config_file)

    def test_sample_config_creation(self):
        """Test sample config file creation."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            config_file = f.name

        try:
            SaaSServicesTelemetryAgent.create_sample_config(config_file)

            # Read and verify config
            with open(config_file, 'r') as f:
                config = json.load(f)

            assert "confluent_kafka" in config
            assert "vercel" in config
            assert "docker_hub" in config
            assert "elasticsearch" in config

            # Verify Kafka config
            assert config["confluent_kafka"]["enabled"] is False
            assert "api_key" in config["confluent_kafka"]
            assert "api_secret" in config["confluent_kafka"]

            # Verify Vercel config
            assert config["vercel"]["enabled"] is False
            assert "token" in config["vercel"]

            # Verify Docker Hub config
            assert config["docker_hub"]["enabled"] is False
            assert "username" in config["docker_hub"]
            assert "password" in config["docker_hub"]

            # Verify Elasticsearch config
            assert config["elasticsearch"]["enabled"] is False
            assert "cloud_id" in config["elasticsearch"]
            assert "api_key" in config["elasticsearch"]
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

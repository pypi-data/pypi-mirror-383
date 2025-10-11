"""
Basic tests for Apiframe client
"""

import pytest

from apiframe import Apiframe, ApiframeError


def test_client_initialization():
    """Test client initialization"""
    client = Apiframe(api_key="test_key")
    assert client is not None


def test_client_requires_api_key():
    """Test that client requires API key"""
    with pytest.raises(ApiframeError):
        Apiframe(api_key="")


def test_client_context_manager():
    """Test context manager usage"""
    with Apiframe(api_key="test_key") as client:
        assert client is not None


def test_client_has_services():
    """Test that client has all services initialized"""
    client = Apiframe(api_key="test_key")
    
    assert hasattr(client, "tasks")
    assert hasattr(client, "midjourney")
    assert hasattr(client, "midjourney_alt")
    assert hasattr(client, "flux")
    assert hasattr(client, "ideogram")
    assert hasattr(client, "luma")
    assert hasattr(client, "suno")
    assert hasattr(client, "udio")
    assert hasattr(client, "runway")
    assert hasattr(client, "kling")
    assert hasattr(client, "ai_photos")
    assert hasattr(client, "media")


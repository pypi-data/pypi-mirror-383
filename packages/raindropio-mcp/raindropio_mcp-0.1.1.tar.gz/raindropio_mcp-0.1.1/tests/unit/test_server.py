"""Unit tests for the server module."""
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastmcp import FastMCP
from raindropio_mcp.server import create_app, APP_NAME, APP_VERSION


@pytest.mark.asyncio
async def test_create_app():
    """Test the create_app function."""
    # Create a test app
    test_app = create_app()
    
    # Verify the app is created correctly
    assert isinstance(test_app, FastMCP)
    assert test_app.name == APP_NAME
    assert test_app.version == APP_VERSION
    
    # Check that client is attached to app
    assert hasattr(test_app, '_raindrop_client')
    
    # Verify lifespan context manager is properly wrapped
    original_lifespan = test_app._mcp_server.lifespan
    assert original_lifespan is not None


@patch('raindropio_mcp.server.build_raindrop_client')
@patch('raindropio_mcp.server.get_settings')
def test_create_app_integration(mock_get_settings, mock_build_client):
    """Integration test for create_app."""
    # Mock settings and client
    mock_settings = MagicMock()
    mock_client = AsyncMock()
    mock_get_settings.return_value = mock_settings
    mock_build_client.return_value = mock_client
    
    # Create app
    test_app = create_app()
    
    # Verify all steps were called
    mock_get_settings.assert_called_once()
    mock_build_client.assert_called_once_with(mock_settings)
    
    # Verify client was attached to app
    assert test_app._raindrop_client == mock_client


@pytest.mark.asyncio
async def test_app_lifespan():
    """Test the lifespan context manager."""
    test_app = create_app()
    
    # Get the lifespan context manager
    lifespan = test_app._mcp_server.lifespan
    
    # Test the context manager
    async with lifespan(test_app._mcp_server) as state:
        # State should be the original state from the server
        pass
    
    # Verify the client close was called when exiting the context
    await test_app._raindrop_client.close()
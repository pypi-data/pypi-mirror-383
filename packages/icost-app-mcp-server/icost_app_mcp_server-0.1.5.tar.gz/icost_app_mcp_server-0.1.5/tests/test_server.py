"""
Tests for the MCP Server module.
"""

import unittest
from unittest.mock import patch, MagicMock

from icost_app_mcp_server.server import MCPServer


class TestMCPServer(unittest.TestCase):
    """Test cases for MCPServer class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.server = MCPServer()
    
    def test_server_initialization(self):
        """Test server initialization with default config."""
        self.assertIsInstance(self.server, MCPServer)
        self.assertEqual(self.server.config, {})
    
    def test_server_initialization_with_config(self):
        """Test server initialization with custom config."""
        config = {"host": "localhost", "port": 8080}
        server = MCPServer(config)
        self.assertEqual(server.config, config)
    
    @patch('icost_app_mcp_server.server.logging')
    def test_setup_logging(self, mock_logging):
        """Test logging setup."""
        server = MCPServer()
        mock_logging.basicConfig.assert_called_once()
    
    def test_start_server(self):
        """Test server start method."""
        with patch.object(self.server.logger, 'info') as mock_info:
            self.server.start()
            mock_info.assert_called_with("Starting iCost MCP Server...")
    
    def test_stop_server(self):
        """Test server stop method."""
        with patch.object(self.server.logger, 'info') as mock_info:
            self.server.stop()
            mock_info.assert_called_with("Stopping iCost MCP Server...")


if __name__ == '__main__':
    unittest.main()
"""Smoke tests for the MCP adapter.

Skipped when the optional `mcp` extra is not installed. CI installs `.[dev,mcp]`
and also constructs the server explicitly, so an SDK major-version break (such
as mcp 2.x renaming FastMCP to MCPServer) fails the build instead of the VPS.
"""
import pytest

pytest.importorskip("mcp.server.fastmcp", reason="mcp extra not installed")


def test_mcp_server_constructs():
    from ats_auditor.mcp_server import create_mcp

    server = create_mcp()
    assert server is not None

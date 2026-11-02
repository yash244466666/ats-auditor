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


SYNTHETIC_RESUME = (
    "Alex Example is a software engineer with five years of production experience. "
    "Built Python FastAPI services, PostgreSQL data models, and React TypeScript "
    "dashboards for fictional organizations. Worked with Docker, GitHub Actions, "
    "pytest, AWS services, SQL performance tuning, security reviews and Agile "
    "teams. Delivered REST API integrations and maintained CI/CD deployments."
)

SYNTHETIC_JOB = (
    "Seeking a mid-level software engineer with at least four years experience "
    "building Python FastAPI REST APIs, PostgreSQL services, Docker images, "
    "automated pytest test suites, GitHub Actions CI/CD pipelines, and React "
    "TypeScript user interfaces. Experience with AWS, Agile collaboration, "
    "code review, application security, troubleshooting and SQL optimization "
    "is strongly preferred."
)


@pytest.mark.parametrize("name", ["get_resume_ats_score", "compare_resume_quality"])
def test_mcp_tool_returns_text_and_structured_score(name, monkeypatch):
    """Exercise a real MCP client/server call, not just server construction."""
    import asyncio

    from mcp.shared.memory import create_connected_server_and_client_session
    from mcp.types import TextContent
    from ats_auditor.mcp_server import create_mcp

    monkeypatch.setenv("ATS_DEPLOYMENT_MODE", "production")

    async def run():
        server = create_mcp()
        async with create_connected_server_and_client_session(server._mcp_server) as client:
            return await client.call_tool(
                name,
                {"resume_text": SYNTHETIC_RESUME, "job_description": SYNTHETIC_JOB},
            )

    result = asyncio.run(run())
    assert result.isError is not True, result
    assert result.content
    assert isinstance(result.content[0], TextContent)
    assert "Overall Score:" in result.content[0].text
    assert result.structuredContent
    assert 0 <= result.structuredContent["overall_score"] <= 100
    assert result.structuredContent["keywords"]
    assert result.structuredContent["content"] == result.content[0].text


@pytest.mark.parametrize('name,mode', [
    ('get_resume_ats_score', 'evidence'), ('get_resume_ats_score', 'requirement_fit'),
    ('compare_resume_quality', None),
])
@pytest.mark.parametrize('variant', ['negated', 'copied'])
def test_mcp_explains_excluded_evidence_over_actual_transport(name, mode, variant, monkeypatch):
    import asyncio
    from mcp.shared.memory import create_connected_server_and_client_session
    from ats_auditor.mcp_server import create_mcp
    from test_evidence_integrity import PROFILE, JOB

    monkeypatch.setenv('ATS_DEPLOYMENT_MODE', 'production')
    resume = PROFILE + '\nEXPERIENCE\n' + ('I have never used Python.' if variant == 'negated' else JOB)
    arguments = {'resume_text': resume, 'job_description': JOB}
    if mode:
        arguments['scoring_mode'] = mode

    async def run():
        server = create_mcp()
        async with create_connected_server_and_client_session(server._mcp_server) as client:
            result = await client.call_tool(name, arguments)
            missing = await client.call_tool('get_resume_ats_score', {'job_description_id': 'not-authentication'})
            return result, missing

    result, missing = asyncio.run(run())
    assert result.isError is not True
    item = next(k for k in result.structuredContent['keywords'] if k['keyword'].casefold() == 'python')
    assert item['present'] is False and item['score'] == 0
    assert 'Evidence notes' in result.content[0].text
    assert result.content[0].text == result.structuredContent['content']
    assert missing.isError is True

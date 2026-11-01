from pathlib import Path
import tomllib

ROOT = Path(__file__).parents[1]


def test_mcp_package_and_nonroot_docker():
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())
    assert 'mcp' in project['project']['optional-dependencies']
    # The server targets the mcp 1.x FastMCP API; 2.x renamed it to MCPServer.
    assert any(spec.startswith('mcp') and '<2' in spec
               for spec in project['project']['optional-dependencies']['mcp'])
    dockerfile = (ROOT / 'Dockerfile').read_text()
    assert 'USER 10001:10001' in dockerfile
    assert 'HEALTHCHECK' in dockerfile


def test_staging_production_deploy_uses_forced_command_and_limited_ports():
    ci = (ROOT / '.github/workflows/ci.yml').read_text()
    deploy = (ROOT / '.github/workflows/deploy.yml').read_text()
    compose = (ROOT / 'deploy/compose.yml').read_text()
    gate = (ROOT / 'deploy/ats-deploy.sh').read_text()
    assert 'branches: [main, dev]' in ci
    assert 'workflow_run' in deploy and "github.event.workflow_run.event == 'push'" in deploy
    # Key-based deploy through a forced command, never a password or a shell.
    assert 'VPS_SSH_KEY' in deploy and 'VPS_SSH_KNOWN_HOSTS' in deploy
    assert 'VPS_SSH_PASSWORD' not in deploy and 'sshpass' not in deploy
    assert 'StrictHostKeyChecking=yes' in deploy
    assert 'deploy $DEPLOY_ENV' in deploy
    assert '127.0.0.1:${PUBLISH_PORT:-8800}:8000' in compose
    assert 'cap_drop:' in compose and 'read_only: true' in compose
    # Gate only accepts the two release targets and pins their loopback ports.
    assert 'deploy production' in gate and 'deploy staging' in gate
    assert 'PORT=8800' in gate and 'PORT=8801' in gate
    assert '/opt/ats-auditor/' in gate


def test_public_mcp_route_is_proxied_with_a_body_limit():
    caddy = (ROOT / 'deploy/Caddyfile').read_text()
    assert 'atsmcp.yashcodes.com' in caddy
    assert 'reverse_proxy 127.0.0.1:8800' in caddy
    assert 'max_size 2MB' in caddy
    # Staging stays on loopback.
    assert 'reverse_proxy 127.0.0.1:8801' not in caddy

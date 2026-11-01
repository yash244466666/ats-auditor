from pathlib import Path
import tomllib

ROOT = Path(__file__).parents[1]


def test_mcp_package_and_nonroot_docker():
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())
    assert 'mcp' in project['project']['optional-dependencies']
    dockerfile = (ROOT / 'Dockerfile').read_text()
    assert 'USER 10001:10001' in dockerfile
    assert 'HEALTHCHECK' in dockerfile


def test_staging_production_pinned_ssh_and_limited_ports():
    ci = (ROOT / '.github/workflows/ci.yml').read_text()
    deploy = (ROOT / '.github/workflows/deploy.yml').read_text()
    compose = (ROOT / 'deploy/compose.yml').read_text()
    assert 'branches: [main, dev]' in ci
    assert 'workflow_run' in deploy and "github.event.workflow_run.event == 'push'" in deploy
    assert 'VPS_SSH_PASSWORD' in deploy and 'VPS_SSH_KNOWN_HOSTS' in deploy
    assert 'sshpass -e' in deploy and 'PubkeyAuthentication=no' in deploy
    assert 'VPS_SSH_KEY' not in deploy
    assert 'StrictHostKeyChecking=yes' in deploy
    assert 'PUBLISH_PORT=8800' in deploy and 'PUBLISH_PORT=8801' in deploy
    assert '127.0.0.1:${PUBLISH_PORT:-8800}:8000' in compose
    assert 'cap_drop:' in compose and 'read_only: true' in compose


def test_public_mcp_not_exposed_without_auth():
    caddy = (ROOT / 'deploy/Caddyfile').read_text()
    assert 'atsmcp.yashcodes.com' in caddy
    assert 'respond "MCP authentication not yet configured" 403' in caddy

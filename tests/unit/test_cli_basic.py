from pathlib import Path

import yaml
from typer.testing import CliRunner

from mesh_wizard import cli

runner = CliRunner()


def test_cli_validate_command(tmp_path):
    mesh_file = tmp_path / "mesh.yaml"
    with mesh_file.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(
            {
                "mesh": {"name": "demo"},
                "nodes": [{"id": "vps", "role": "public_vps"}],
                "services": [{"id": "svc", "type": "http", "node": "vps"}],
            },
            fh,
            sort_keys=False,
        )
    result = runner.invoke(cli.app, ["validate", str(mesh_file)])
    assert result.exit_code == 0


def test_cli_diagram(tmp_path):
    mesh_path = Path("examples/simple-single-vps.yaml")
    result = runner.invoke(cli.app, ["diagram", str(mesh_path)])
    assert result.exit_code == 0
    assert "Cloudflare" in result.stdout

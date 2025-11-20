from typer.testing import CliRunner

from mesh_wizard import cli

runner = CliRunner()


def test_render_multi_segment(tmp_path):
    out_dir = tmp_path / "out"
    result = runner.invoke(
        cli.app,
        ["render", "examples/multi-vps-k3s-lan.yaml", "--out", str(out_dir)],
    )
    assert result.exit_code == 0
    frp_dir = out_dir / "frp"
    assert frp_dir.exists()
    assert any(name.name.endswith("frpc.toml") for name in frp_dir.glob("*.toml"))
    traefik_dir = out_dir / "traefik"
    assert traefik_dir.exists()
    assert any("dynamic" in path.name for path in traefik_dir.glob("*.yaml"))

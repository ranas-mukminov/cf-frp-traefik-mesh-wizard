from typer.testing import CliRunner

from mesh_wizard import cli

runner = CliRunner()


def test_render_simple_topology(tmp_path):
    out_dir = tmp_path / "out"
    result = runner.invoke(
        cli.app,
        ["render", "examples/simple-single-vps.yaml", "--out", str(out_dir)],
    )
    assert result.exit_code == 0
    assert (out_dir / "cloudflare" / "config.yaml").exists()
    frp_dir = out_dir / "frp"
    assert frp_dir.exists()
    assert any(path.name.endswith("frps.toml") for path in frp_dir.glob("*.toml"))

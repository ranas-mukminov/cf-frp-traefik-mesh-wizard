"""Command line interface for mesh wizard."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console

from . import __version__
from .generators import (
    cloudflare_generator,
    diagram_generator,
    frp_client_generator,
    frp_server_generator,
    traefik_dynamic_generator,
    traefik_static_generator,
)
from .loader import load_raw, load_topology

app = typer.Typer(help="Cloudflare + FRP + Traefik mesh wizard")
console = Console()


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        fh.write(content)


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(False, "--version", "-v", help="Show version"),
) -> None:
    """Root callback to expose --version."""
    if version:
        console.print(f"cf-frp-traefik-mesh-wizard {__version__}")
        raise typer.Exit()


@app.command()
def init(path: Path = typer.Argument(default="mesh.yaml")):
    """Scaffold a minimal mesh YAML."""
    if path.exists():
        typer.confirm(f"{path} exists, overwrite?", abort=True)
    template = {
        "mesh": {"name": "sample-mesh", "description": "Edit me"},
        "cloudflare": {
            "account_id": "CF_ACCOUNT_ID",
            "tunnel_name": "sample-tunnel",
            "zone": "example.com",
            "dns": [
                {
                    "hostname": "apps.example.com",
                    "entrypoint": "websecure",
                    "target": "service://apps-router",
                }
            ],
        },
        "nodes": [
            {
                "id": "vps",
                "role": "public_vps",
                "public_ip": "203.0.113.10",
                "frp": {
                    "server": True,
                    "bind_port": 7000,
                    "vhost_http_port": 19080,
                    "vhost_https_port": 19443,
                    "token": "CHANGE_ME",
                },
                "traefik": {
                    "enabled": True,
                    "entrypoints": [
                        {"name": "web", "port": 80},
                        {"name": "websecure", "port": 443},
                    ],
                },
            }
        ],
        "services": [
            {
                "id": "apps-router",
                "type": "http",
                "node": "vps",
                "via": "traefik",
                "router": {
                    "rule": "Host(`apps.example.com`)",
                    "entrypoints": ["websecure"],
                    "service": "apps-service",
                    "tls": True,
                },
                "backend": {"type": "frp_http", "proxy_name": "apps-http"},
            }
        ],
    }
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(template, fh, sort_keys=False)
    console.print(f"Scaffolded {path}")


@app.command()
def validate(mesh_file: Path):
    """Validate mesh YAML against schema and semantics."""
    load_raw(mesh_file)
    console.print("Mesh file is valid ✅")


@app.command()
def plan(mesh_file: Path):
    """Show a plan of configs that would be generated."""
    topology = load_topology(mesh_file)
    console.print(f"Mesh: {topology.mesh.name}")
    console.print(f"Nodes: {', '.join(topology.nodes.keys())}")
    console.print("Services:")
    for service in topology.services.values():
        console.print(f" • {service.id} ({service.type}) via {service.via} @ {service.node}")
    console.print("Artifacts:")
    console.print(f" - Cloudflare config: {'yes' if topology.cloudflare else 'no'}")
    frp_servers = sum(1 for node in topology.nodes.values() if node.frp and node.frp.server)
    console.print(f" - FRP servers: {frp_servers}")
    frp_clients = sum(1 for node in topology.nodes.values() if node.frp and node.frp.client)
    console.print(f" - FRP clients: {frp_clients}")
    traefik_count = sum(
        1 for node in topology.nodes.values() if node.traefik and node.traefik.enabled
    )
    console.print(f" - Traefik nodes: {traefik_count}")


@app.command()
def render(
    mesh_file: Path,
    out: Path = typer.Option(default="out", help="Output directory"),
):
    """Generate configs into an output directory."""
    topology = load_topology(mesh_file)
    out.mkdir(parents=True, exist_ok=True)
    if topology.cloudflare:
        cf_config = cloudflare_generator.generate(topology)
        _write_yaml(out / "cloudflare" / "config.yaml", cf_config)
    frps = frp_server_generator.generate(topology)
    for name, content in frps.items():
        _write_text(out / "frp" / name, content)
    frpc = frp_client_generator.generate(topology)
    for name, content in frpc.items():
        _write_text(out / "frp" / name, content)
    static_configs = traefik_static_generator.generate(topology)
    for name, config in static_configs.items():
        _write_yaml(out / "traefik" / name, config)
    dynamic_configs = traefik_dynamic_generator.generate(topology)
    for name, config in dynamic_configs.items():
        _write_yaml(out / "traefik" / name, config)
    console.print(f"Configs written to {out}")


@app.command()
def diagram(mesh_file: Path):
    """Print an ASCII diagram of the mesh."""
    topology = load_topology(mesh_file)
    art = diagram_generator.build_ascii(topology)
    console.print(art)


def _lazy_import_ai():  # pragma: no cover - optional dependency
    from .ai import ha_suggestions, topology_nl_to_yaml

    return topology_nl_to_yaml, ha_suggestions


@app.command("ai-suggest")
def ai_suggest(from_text: Path, out: Path = typer.Argument(default="mesh-ai.yaml")):
    """Generate a draft mesh YAML from natural language description."""
    topology_nl_to_yaml, _ = _lazy_import_ai()
    description = from_text.read_text(encoding="utf-8")
    draft = topology_nl_to_yaml.generate_from_text(description)
    _write_yaml(out, draft)
    console.print(f"AI draft written to {out}")


@app.command("ai-ha")
def ai_ha(mesh_file: Path, out: Path = typer.Argument(default="ha-plan.md")):
    """Request HA / failover suggestions for an existing mesh."""
    _, ha_suggestions = _lazy_import_ai()
    topology = load_topology(mesh_file)
    plan = ha_suggestions.generate(topology)
    out.write_text(plan.report, encoding="utf-8")
    console.print(f"HA report written to {out}")


if __name__ == "__main__":
    app()

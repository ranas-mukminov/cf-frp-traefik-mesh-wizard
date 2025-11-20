"""HA / failover helper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ai_providers.base import AIProvider, registry

from ..model import MeshTopology


@dataclass
class HAPlan:
    suggestions: List[str]
    report: str


def _build_prompt(topology: MeshTopology) -> str:
    public_nodes = [node.id for node in topology.nodes.values() if node.role == "public_vps"]
    lan_nodes = [node.id for node in topology.nodes.values() if node.role != "public_vps"]
    return (
        "Suggest high availability improvements for the following mesh:\n"
        f"Public nodes: {public_nodes}\n"
        f"LAN nodes: {lan_nodes}\n"
        f"Services: {[service.id for service in topology.services.values()]}\n"
        "Recommend redundant ingress, backup tunnels, and health checks."
    )


def generate(topology: MeshTopology, *, provider: Optional[AIProvider] = None) -> HAPlan:
    provider = provider or registry.require()
    response = provider.complete(_build_prompt(topology), temperature=0.1)
    suggestions = [line.strip("- ") for line in response.splitlines() if line.strip()]
    markdown_lines = ["## HA / Failover suggestions", ""]
    for item in suggestions:
        markdown_lines.append(f"- {item}")
    report = "\n".join(markdown_lines) + "\n"
    return HAPlan(suggestions=suggestions, report=report)

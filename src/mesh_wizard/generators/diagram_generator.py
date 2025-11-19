"""ASCII diagram generator for mesh topologies."""
from __future__ import annotations

from typing import List

from ..model import MeshTopology, Service


def _describe_service(service: Service) -> str:
    target = ""
    if service.backend and service.backend.proxy_name:
        target = f"proxy {service.backend.proxy_name}"
    elif service.target and service.target.node:
        target = f"node {service.target.node}:{service.target.port or ''}"
    return f"{service.id} [{service.type}] via {service.via} -> {target or 'unspecified'}"


def build_ascii(topology: MeshTopology) -> str:
    lines: List[str] = ["[Internet]"]
    if topology.cloudflare:
        zone = topology.cloudflare.zone or "Cloudflare"
        lines.extend([
            "   |",
            f"[ Cloudflare DNS ({zone}) ]",
            "   |",
            f"[ Cloudflare Tunnel: {topology.cloudflare.tunnel_name} ]",
        ])
    for node in topology.nodes.values():
        label = f"[ Node {node.id} ({node.role}) ]"
        lines.extend(["   |", label])
        attached = [svc for svc in topology.services.values() if svc.node == node.id]
        for svc in attached:
            lines.append(f"   |--> {_describe_service(svc)}")
    return "\n".join(lines)

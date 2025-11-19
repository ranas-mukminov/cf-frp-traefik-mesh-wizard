"""Cloudflare Tunnel config generator."""
from __future__ import annotations

from typing import Dict, List

from ..model import DNSMapping, MeshTopology, Node, Service


class CloudflareConfigError(RuntimeError):
    """Raised when Cloudflare config cannot be produced."""


def _resolve_service(topology: MeshTopology, target: str) -> Service:
    if target.startswith("service://"):
        service_id = target.split("service://", 1)[1]
    else:
        service_id = target
    return topology.require_service(service_id)


def _entrypoint_port(node: Node, entrypoint_name: str | None) -> int:
    if not entrypoint_name:
        return 443
    if node.traefik:
        for entrypoint in node.traefik.entrypoints:
            if entrypoint.name == entrypoint_name:
                return entrypoint.port
    if entrypoint_name.lower() in {"web", "http"}:
        return 80
    if entrypoint_name.lower() in {"websecure", "https"}:
        return 443
    return 443


def _entrypoint_scheme(entrypoint_name: str | None, service: Service) -> str:
    if service.router and service.router.tls:
        return "https"
    if entrypoint_name and "secure" in entrypoint_name.lower():
        return "https"
    return "http"


def _build_ingress_item(topology: MeshTopology, mapping: DNSMapping) -> Dict[str, Any]:
    service = _resolve_service(topology, mapping.target)
    node = topology.get_node(service.node)
    entrypoint_name = mapping.entrypoint
    scheme = _entrypoint_scheme(entrypoint_name, service)
    port = _entrypoint_port(node, entrypoint_name)
    hostname = mapping.hostname
    host_hint = node.public_ip or node.id
    service_url = f"{scheme}://{host_hint}:{port}"
    return {"hostname": hostname, "service": service_url}


def generate(topology: MeshTopology) -> Dict[str, Any]:
    cloudflare = topology.cloudflare
    if not cloudflare:
        raise CloudflareConfigError("Mesh does not define Cloudflare configuration")
    ingress: List[Dict[str, Any]] = []
    for mapping in cloudflare.dns:
        ingress.append(_build_ingress_item(topology, mapping))
    ingress.append({"service": "http_status:404"})
    credentials_path = cloudflare.credentials_file or f"/etc/cloudflared/{cloudflare.tunnel_name}.json"
    return {
        "tunnel": cloudflare.tunnel_name,
        "credentials-file": credentials_path,
        "ingress": ingress,
    }

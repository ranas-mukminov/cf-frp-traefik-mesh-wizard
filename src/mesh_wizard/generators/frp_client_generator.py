"""FRP client config generator."""
from __future__ import annotations

from typing import Dict

from ..model import FRPConfig, MeshTopology, Node


class FRPClientConfigError(RuntimeError):
    """Raised when FRP client config is invalid."""


def _resolve_server_address(topology: MeshTopology, value: str | None) -> str:
    if not value:
        raise FRPClientConfigError("FRP client must define server_addr")
    if value in topology.nodes and topology.nodes[value].public_ip:
        return topology.nodes[value].public_ip  # type: ignore[return-value]
    return value


def _render_proxy(proxy) -> str:
    lines = [
        "[[proxies]]",
        f"name = \"{proxy.name}\"",
        f"type = \"{proxy.type}\"",
        f"localIP = \"{proxy.local_ip}\"",
        f"localPort = {proxy.local_port}",
    ]
    if proxy.remote_port:
        lines.append(f"remotePort = {proxy.remote_port}")
    if proxy.custom_domains:
        domains = ", ".join(f'\"{domain}\"' for domain in proxy.custom_domains)
        lines.append(f"customDomains = [{domains}]")
    if proxy.subdomain:
        lines.append(f"subdomain = \"{proxy.subdomain}\"")
    return "\n".join(lines)


def _render_client(node: Node, topology: MeshTopology) -> str:
    frp: FRPConfig = node.frp or FRPConfig()
    if not frp.token:
        raise FRPClientConfigError(f"Node {node.id} FRP client requires an auth token")
    server_addr = _resolve_server_address(topology, frp.server_addr)
    server_port = frp.server_port or 7000
    header = [
        f"serverAddr = \"{server_addr}\"",
        f"serverPort = {server_port}",
        "auth.method = \"token\"",
        f"auth.token = \"{frp.token}\"",
    ]
    proxy_blocks = [
        _render_proxy(proxy)
        for proxy in frp.proxies
    ] or ["# Define proxies in mesh YAML"]
    return "\n".join(header + ["", *proxy_blocks, ""]).strip() + "\n"


def generate(topology: MeshTopology) -> Dict[str, str]:
    configs: Dict[str, str] = {}
    for node in topology.nodes.values():
        if node.frp and node.frp.client:
            configs[f"{node.id}-frpc.toml"] = _render_client(node, topology)
    return configs

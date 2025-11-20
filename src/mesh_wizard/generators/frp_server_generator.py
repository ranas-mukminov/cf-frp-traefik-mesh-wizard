"""FRP server config generator."""

from __future__ import annotations

from typing import Dict

from ..model import FRPConfig, MeshTopology, Node

DEFAULT_LOG_LEVEL = "info"


def _require_server(node: Node) -> None:
    if not node.frp or not node.frp.server:
        raise ValueError(f"Node {node.id} is not configured as an FRP server")
    if not node.frp.token:
        raise ValueError(f"Node {node.id} FRP server requires an auth token")


def _render_server(node: Node) -> str:
    frp: FRPConfig = node.frp or FRPConfig()
    bind_port = frp.bind_port or 7000
    vhost_http = frp.vhost_http_port or 19080
    vhost_https = frp.vhost_https_port or 19443
    token = frp.token or "CHANGE_ME_SECURE_TOKEN"
    lines = [
        'bindAddr = "0.0.0.0"',
        f"bindPort = {bind_port}",
        f"vhostHTTPPort = {vhost_http}",
        f"vhostHTTPSPort = {vhost_https}",
        'auth.method = "token"',
        f'auth.token = "{token}"',
        "transport.maxPoolCount = 5",
        "transport.heartbeatTimeout = 90",
        'log.to = "console"',
        f'log.level = "{DEFAULT_LOG_LEVEL}"',
    ]
    return "\n".join(lines) + "\n"


def generate(topology: MeshTopology) -> Dict[str, str]:
    configs: Dict[str, str] = {}
    for node in topology.nodes.values():
        if node.frp and node.frp.server:
            _require_server(node)
            configs[f"{node.id}-frps.toml"] = _render_server(node)
    return configs

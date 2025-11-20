"""Traefik static configuration generator."""

from __future__ import annotations

from typing import Dict

from ..model import MeshTopology, Node

DEFAULT_PROVIDER_DIR = "/etc/traefik/dynamic"


def _render_entrypoints(node: Node) -> Dict[str, Dict[str, str]]:
    if not node.traefik:
        return {}
    entrypoints: Dict[str, Dict[str, str]] = {}
    for entrypoint in node.traefik.entrypoints:
        entrypoints[entrypoint.name] = {"address": f":{entrypoint.port}"}
    if not entrypoints:
        entrypoints["web"] = {"address": ":80"}
        entrypoints["websecure"] = {"address": ":443"}
    return entrypoints


def generate(topology: MeshTopology) -> Dict[str, Dict[str, object]]:
    configs: Dict[str, Dict[str, object]] = {}
    for node in topology.nodes.values():
        if not node.traefik or not node.traefik.enabled:
            continue
        entrypoints = _render_entrypoints(node)
        provider_dir = node.traefik.provider_directory or DEFAULT_PROVIDER_DIR
        config = {
            "entryPoints": entrypoints,
            "providers": {
                "file": {
                    "directory": provider_dir,
                    "watch": True,
                }
            },
            "log": {"level": node.traefik.log_level or "INFO"},
        }
        configs[f"{node.id}-traefik-static.yaml"] = config
    return configs

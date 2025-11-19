"""AI-assisted topology scaffolding."""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from ai_providers.base import AIProvider, registry

DEFAULT_TOKEN = "REPLACE_WITH_STRONG_TOKEN"


def _extract_hostnames(text: str) -> List[str]:
    pattern = re.compile(r"[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    hosts = []
    for match in pattern.findall(text):
        if match not in hosts:
            hosts.append(match)
    return hosts or ["apps.example.com"]


def generate_from_text(description: str, *, provider: Optional[AIProvider] = None) -> Dict[str, object]:
    """Generate a draft mesh YAML dict from text using an AI hint."""
    provider = provider or registry.require()
    ai_hint = provider.complete(
        "Summarize services and domains from the following topology description:\n" + description,
        temperature=0.1,
    )
    combined = f"{description}\n{ai_hint}"
    hostnames = _extract_hostnames(combined)
    mesh_name = hostnames[0].split(".")[0].replace("-", "_")
    dns_entries = [
        {
            "hostname": host,
            "entrypoint": "websecure",
            "target": f"service://{host.split('.')[0]}-router",
        }
        for host in hostnames
    ]
    services = [
        {
            "id": f"{host.split('.')[0]}-router",
            "type": "http",
            "node": "vps",
            "via": "traefik",
            "router": {
                "rule": f"Host(`{host}`)",
                "entrypoints": ["websecure"],
                "service": f"{host.split('.')[0]}-service",
                "tls": True,
            },
            "backend": {
                "type": "frp_http",
                "proxy_name": f"{host.split('.')[0]}-http",
            },
        }
        for host in hostnames
    ]
    return {
        "mesh": {"name": f"{mesh_name}-mesh", "description": "AI-drafted mesh"},
        "cloudflare": {
            "account_id": "CF_ACCOUNT",
            "tunnel_name": f"{mesh_name}-tunnel",
            "zone": hostnames[0].split(".", 1)[1],
            "dns": dns_entries,
        },
        "nodes": [
            {
                "id": "vps",
                "role": "public_vps",
                "public_ip": "198.51.100.10",
                "frp": {
                    "server": True,
                    "bind_port": 7000,
                    "vhost_http_port": 19080,
                    "vhost_https_port": 19443,
                    "token": DEFAULT_TOKEN,
                },
                "traefik": {
                    "enabled": True,
                    "entrypoints": [
                        {"name": "web", "port": 80},
                        {"name": "websecure", "port": 443},
                    ],
                },
            },
            {
                "id": "lan-cluster",
                "role": "lan_cluster",
                "lan_ip": "192.168.1.10",
                "frp": {
                    "client": True,
                    "server_addr": "vps",
                    "server_port": 7000,
                    "token": DEFAULT_TOKEN,
                    "proxies": [
                        {
                            "name": f"{hostnames[0].split('.')[0]}-http",
                            "type": "http",
                            "local_ip": "10.42.0.10",
                            "local_port": 8080,
                            "custom_domains": hostnames,
                        }
                    ],
                },
            },
        ],
        "services": services,
    }

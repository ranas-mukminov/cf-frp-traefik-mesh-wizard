#!/usr/bin/env bash
set -euo pipefail

tmp_dir=$(mktemp -d)
mesh_file="$tmp_dir/mesh.yaml"
out_dir="$tmp_dir/out"

python - "$mesh_file" <<'PY'
import sys
from pathlib import Path

import yaml

mesh_path = Path(sys.argv[1])

nodes = []
services = []
for idx in range(1, 51):
    nodes.append(
        {
            "id": f"vps{idx}",
            "role": "public_vps",
            "frp": {"server": True, "token": f"TOKEN{idx}", "bind_port": 7000 + idx},
            "traefik": {
                "enabled": True,
                "entrypoints": [
                    {"name": "web", "port": 80},
                    {"name": "websecure", "port": 443},
                ],
            },
        }
    )
for idx in range(1, 201):
    services.append(
        {
            "id": f"svc{idx}",
            "type": "http",
            "node": "vps1",
            "via": "traefik",
            "router": {
                "rule": f"Host(`svc{idx}.example.com`)",
                "entrypoints": ["websecure"],
                "service": f"svc{idx}-service",
                "tls": True,
            },
            "backend": {"type": "static_url", "url": "http://127.0.0.1:8080"},
        }
    )
mesh = {
    "mesh": {"name": "perf-mesh"},
    "cloudflare": {
        "account_id": "CF",
        "tunnel_name": "perf",
        "dns": [
            {"hostname": f"svc{idx}.example.com", "entrypoint": "websecure", "target": f"service://svc{idx}"}
            for idx in range(1, 11)
        ],
    },
    "nodes": nodes,
    "services": services,
}
mesh_path.write_text(yaml.safe_dump(mesh, sort_keys=False), encoding="utf-8")
PY

time mesh-wizard render "$mesh_file" --out "$out_dir"

echo "Artifacts stored in $out_dir"

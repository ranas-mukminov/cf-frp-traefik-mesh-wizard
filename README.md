# cf-frp-traefik-mesh-wizard

![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CI](https://github.com/run-as-daemon/cf-frp-traefik-mesh-wizard/actions/workflows/ci.yml/badge.svg)

## English

### What is this?
`cf-frp-traefik-mesh-wizard` turns one declarative YAML topology file into ready-to-deploy configs for Cloudflare Tunnel (`cloudflared`), FRP (server + clients), and Traefik (static + dynamic). It focuses on realistic chains that traverse a public VPS, Cloudflare access edge, FRP relays, and LAN clusters such as K3s or Docker homelabs.

### Why?
Documentation usually covers Cloudflare Tunnel, Traefik, or FRP separately. When you chain them, it becomes difficult to reason about which layer performed TLS termination, why 404 surfaces, or how to add redundancy. This wizard keeps the topology declarative so you can reproduce and audit complex "Cloudflare → Traefik → FRP → app" paths without bespoke scripts.

### Features
- Single YAML mesh topology validated by JSON Schema.
- Generated configs for `cloudflared`, `frps.toml`, `frpc.toml`, and Traefik static/dynamic files.
- ASCII diagrams visualizing every hop of the chain.
- AI helpers to go from natural language → YAML or to propose HA / failover variants.
- Semantic checks that encourage safe defaults (FRP auth tokens, catch-all Cloudflare ingress rules, TLS-ready Traefik routers).

### Quick start
1. **Install (editable during development):**
   ```bash
   pip install -e .
   ```
2. **Create a mesh file** using `mesh-wizard init` or copy from `examples/`.
3. **Validate it:**
   ```bash
   mesh-wizard validate mesh.yaml
   ```
4. **Render configs:**
   ```bash
   mesh-wizard render mesh.yaml --out ./out
   ```
5. **Review and deploy** generated files on the appropriate nodes (VPS, LAN clients, cluster controllers).

> ℹ️ AI subcommands (`ai-suggest`, `ai-ha`) require configuring a provider, e.g.:
> ```python
> from ai_providers.openai_provider import OpenAIProvider
> from ai_providers.base import registry
> registry.configure(OpenAIProvider(api_key=\"...\"))  # placed in your tooling bootstrap
> ```

### Mesh YAML basics
- `mesh`: name/description metadata.
- `cloudflare`: account / tunnel settings and DNS to entrypoint mapping.
- `nodes`: public VPS, FRP hubs, LAN clusters, edge devices with their roles and services.
- `services`: routing intent explaining how routers, FRP proxies, and Traefik link together.
See `schema/mesh-schema.yaml` and the `examples/` directory for full references.

### Security
- Replace placeholder tokens and credentials with secrets sourced from vaults or environment variables.
- Apply Cloudflare Access / firewall policies and FRP auth on every exposed tunnel.
- Never publish admin endpoints directly; prefer allow-listed hostnames and TLS-ready routers.

### Legal / responsible use
Operate only on infrastructure you own or have authorization to manage. Respect the terms of Cloudflare, FRP, Traefik, and your hosting provider. The project automates legitimate configuration workflows and must not be used to bypass firewalls or violate acceptable use policies.

### Professional services – run-as-daemon.ru
> **Professional services by [run-as-daemon.ru](https://run-as-daemon.ru)**
> Maintained by the DevSecOps / SRE engineer behind run-as-daemon.ru. If you need help designing secure Cloudflare + FRP + Traefik meshes, migrating brownfield deployments into declarative configs, or debugging tricky Cloudflare/FRP/TLS handoffs, reach out for consulting, implementation, and production support engagements.

### Contributing
- Use Python 3.10+ with `ruff`, `black`, and `isort`.
- Run `scripts/lint.sh` and `pytest` before sending PRs.
- Keep documentation and examples synchronized with schema changes.

### License
Apache License 2.0. See `LICENSE` for details.

---

## Русский (кратко)

`cf-frp-traefik-mesh-wizard` генерирует конфиги Cloudflare Tunnel, FRP и Traefik из одного YAML-топологии, полезен для homelab и SMB, где публичный VPS связывает Cloudflare и частный K3s/Docker кластер. Инструмент делает проверки безопасности, умеет рисовать ASCII-диаграммы и предлагает AI-подсказки по избыточности. Используйте только на своей инфраструктуре, соблюдайте требования Cloudflare, FRP, Traefik и провайдеров. Нужна помощь в проектировании или внедрении? Обращайтесь через [run-as-daemon.ru](https://run-as-daemon.ru).

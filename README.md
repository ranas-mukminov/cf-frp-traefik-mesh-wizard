# 🧙‍♂️ cf-frp-traefik-mesh-wizard

![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CI](https://github.com/run-as-daemon/cf-frp-traefik-mesh-wizard/actions/workflows/ci.yml/badge.svg)

**Declarative YAML-driven mesh network generator for Cloudflare Tunnel + FRP + Traefik**

_Defense by design. Speed by default._

Turn one declarative YAML topology file into ready-to-deploy configs for Cloudflare Tunnel (`cloudflared`), FRP (server + clients), and Traefik (static + dynamic). Perfect for secure distributed networks, homelabs, and production mesh architectures.

---

## 🎯 Professional Deployment & Support

**Looking for production-grade infrastructure?**

🌐 **[run-as-daemon.ru](https://run-as-daemon.ru)** offers professional services for mesh network architecture, zero-trust security, and infrastructure automation:

- 🌐 **Mesh Network Architecture Design** - Cloudflare Tunnel + FRP + Traefik integration and optimization
- 🔒 **Zero-Trust Network Implementation** - Network segmentation, TLS everywhere, access policies
- 🏗️ **Infrastructure as Code & GitOps** - Automated deployment pipelines and configuration management
- 📊 **High-Availability & Failover Setup** - Multi-node clusters, redundancy, load balancing
- 🤖 **CI/CD & Automation** - Automated config generation, testing, and deployment
- 🛡️ **Security Audits & Hardening** - Mesh security review, vulnerability assessment, remediation
- 📈 **Monitoring & Observability** - Logging, metrics, alerting for distributed systems

💬 **Contact**: [Website](https://run-as-daemon.ru) | [GitHub](https://github.com/ranas-mukminov) | Telegram/WhatsApp via website

_"Defense by design. Speed by default."_

---

## 🌟 What is this?

`cf-frp-traefik-mesh-wizard` is a Python CLI tool that turns a single declarative YAML topology file into ready-to-deploy configurations for:
- **Cloudflare Tunnel** (`cloudflared`) - Secure ingress from the internet
- **FRP** (Fast Reverse Proxy) - Flexible tunneling and port forwarding
- **Traefik** - Modern reverse proxy with dynamic routing

It focuses on realistic chains that traverse public VPS nodes, Cloudflare access edge, FRP relays, and private LAN clusters such as K3s or Docker homelabs.

## 🤔 Why?

Documentation usually covers Cloudflare Tunnel, Traefik, or FRP separately. When you chain them together, it becomes challenging to:
- Reason about which layer performs TLS termination
- Debug why 404 errors surface
- Add redundancy and failover
- Maintain security across the stack

This wizard keeps the topology **declarative** so you can reproduce and audit complex "Cloudflare → Traefik → FRP → app" paths without bespoke scripts.

## ✨ Features

- 📝 **Single YAML Topology** - Define your entire mesh network in one declarative file, validated by JSON Schema
- 🔧 **Multi-Platform Config Generation** - Produces ready-to-deploy configs for `cloudflared`, `frps.toml`, `frpc.toml`, and Traefik static/dynamic files
- 🎨 **Visual Network Diagrams** - ASCII diagrams visualizing every hop of the chain for easy understanding
- 🤖 **AI-Powered Assistance** - Natural language to YAML conversion and HA/failover variant proposals
- 🔒 **Security by Default** - Semantic checks that encourage safe defaults (FRP auth tokens, secure ingress rules, TLS-ready routers)
- 🚀 **Production-Ready** - Designed for real-world deployments from homelabs to enterprise

## 🚀 Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

1. **Create a mesh topology file** using the interactive wizard or copy from examples:
   ```bash
   mesh-wizard init
   # or
   cp examples/simple-single-vps.yaml my-mesh.yaml
   ```

2. **Validate your topology**:
   ```bash
   mesh-wizard validate my-mesh.yaml
   ```

3. **Generate deployment configs**:
   ```bash
   mesh-wizard render my-mesh.yaml --out ./out
   ```

4. **Review and deploy** generated files on the appropriate nodes (VPS, LAN clients, cluster controllers)

> 💡 For a detailed walkthrough, see [QUICKSTART.md](QUICKSTART.md)

### AI Features (Optional)

AI subcommands (`ai-suggest`, `ai-ha`) require configuring a provider:

```python
from ai_providers.openai_provider import OpenAIProvider
from ai_providers.base import registry

registry.configure(OpenAIProvider(api_key="..."))
```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet Users                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                  ┌─────────▼──────────┐
                  │  Cloudflare Edge   │
                  │   (Global CDN)     │
                  └─────────┬──────────┘
                            │
                  ┌─────────▼──────────┐
                  │ Cloudflare Tunnel  │
                  │   (cloudflared)    │
                  └─────────┬──────────┘
                            │
              ┌─────────────▼─────────────┐
              │      Public VPS Node      │
              │  ┌──────────────────────┐ │
              │  │   Traefik Proxy      │ │
              │  │  (Routing & TLS)     │ │
              │  └──────────┬───────────┘ │
              │  ┌──────────▼───────────┐ │
              │  │    FRP Server        │ │
              │  │  (frps, port 7000)   │ │
              │  └──────────┬───────────┘ │
              └─────────────┼─────────────┘
                            │ Encrypted Tunnel
              ┌─────────────▼─────────────┐
              │   Private LAN / Homelab   │
              │  ┌──────────────────────┐ │
              │  │    FRP Client        │ │
              │  │   (frpc)             │ │
              │  └──────────┬───────────┘ │
              │  ┌──────────▼───────────┐ │
              │  │  K3s/Docker/Apps     │ │
              │  │  (Backend Services)  │ │
              │  └──────────────────────┘ │
              └───────────────────────────┘
```

### How It Works

1. **Cloudflare Edge** - Global CDN and DDoS protection
2. **Cloudflare Tunnel** - Secure ingress without exposing IPs
3. **Traefik on VPS** - Dynamic routing, TLS termination, middleware
4. **FRP Layer** - Flexible tunneling between VPS and private networks
5. **Backend Services** - Your applications (K3s, Docker, bare metal)

The wizard generates configs for all these components from a single YAML file.

## 🛠️ Tech Stack

- **Python 3.10+** - Modern Python with type hints
- **Cloudflare Tunnel** - Secure ingress without port forwarding
- **FRP** (Fast Reverse Proxy) - High-performance tunneling
- **Traefik v2/v3** - Cloud-native reverse proxy
- **YAML + JSON Schema** - Declarative configuration with validation
- **Typer + Rich** - Beautiful CLI interface
- **Optional: OpenAI** - AI-powered topology suggestions

## 📋 Mesh YAML Basics

Your mesh topology is defined in a single YAML file with these key sections:

- **`mesh`** - Name and description metadata
- **`cloudflare`** - Account/tunnel settings and DNS to entrypoint mapping
- **`nodes`** - Public VPS, FRP hubs, LAN clusters, edge devices with their roles and services
- **`services`** - Routing intent explaining how routers, FRP proxies, and Traefik link together

See [`schema/mesh-schema.yaml`](schema/mesh-schema.yaml) and the [`examples/`](examples/) directory for full references.

## 📚 Usage Examples

### Simple Single VPS

```yaml
mesh:
  name: single-vps
  description: One public VPS with Cloudflare tunnel feeding Traefik + FRP

cloudflare:
  tunnel_name: vps-homelab
  zone: example.com
  dns:
    - hostname: apps.example.com
      target: service://apps-router

nodes:
  - id: vps-hetzner
    role: public_vps
    public_ip: 203.0.113.10
    frp:
      server: true
      bind_port: 7000
    traefik:
      enabled: true
```

For more examples, see:
- [`examples/simple-single-vps.yaml`](examples/simple-single-vps.yaml)
- [`examples/homelab-k3s-with-mail.yaml`](examples/homelab-k3s-with-mail.yaml)
- [`examples/multi-vps-k3s-lan.yaml`](examples/multi-vps-k3s-lan.yaml)

## 🔒 Security Best Practices

- ✅ **Replace placeholder tokens** with secrets from vaults or environment variables
- ✅ **Use Cloudflare Access policies** and FRP authentication on every exposed tunnel
- ✅ **Enable TLS everywhere** - Use Traefik TLS-ready routers and FRP with encryption
- ✅ **Never expose admin endpoints** directly - Prefer allow-listed hostnames
- ✅ **Follow least privilege** - Only open necessary ports and services
- ✅ **Regular audits** - Review generated configs before deployment

For comprehensive security guidelines, see [SECURITY.md](SECURITY.md)

## 🎓 Professional Deployment Recommendations

### For Production Use

1. **High Availability**
   - Deploy multiple FRP servers behind load balancers
   - Use Traefik clustering for failover
   - Implement health checks and monitoring

2. **Zero-Trust Architecture**
   - Cloudflare Access for authentication
   - Network segmentation with FRP
   - TLS termination at every layer

3. **Infrastructure as Code**
   - Version control your mesh YAML files
   - Automate deployment with CI/CD
   - Use GitOps for configuration management

4. **Monitoring & Observability**
   - Centralized logging (ELK, Loki)
   - Metrics collection (Prometheus)
   - Distributed tracing (Jaeger, Tempo)

5. **Disaster Recovery**
   - Backup configurations regularly
   - Document recovery procedures
   - Test failover scenarios

**Need expert assistance?** Contact [run-as-daemon.ru](https://run-as-daemon.ru) for professional deployment services.

## 📚 Documentation

- 📖 [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- 🚀 [Deployment Guide](DEPLOYMENT.md) - Comprehensive deployment instructions
- 🔒 [Security Policy](SECURITY.md) - Security best practices and reporting
- 🤝 [Contributing Guidelines](CONTRIBUTING.md) - How to contribute
- 📜 [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines
- 📋 [Changelog](CHANGELOG.md) - Release history

## 👨‍💻 Author & Professional Services

Created and maintained by **Ranas Mukminov** ([@ranas-mukminov](https://github.com/ranas-mukminov))

### Professional Services by run-as-daemon.ru

🌐 **[run-as-daemon.ru](https://run-as-daemon.ru)** - _"Defense by design. Speed by default."_

Specialized in DevSecOps, SRE, and infrastructure automation with focus on:

#### 🌐 Mesh Network Architecture
- **Design & Planning** - Custom mesh topology design for your infrastructure
- **Cloudflare Integration** - Tunnel setup, Access policies, DDoS protection
- **FRP Optimization** - High-performance tunneling, multi-site connectivity
- **Traefik Configuration** - Advanced routing, middleware, TLS management

#### 🔒 Zero-Trust Security
- **Network Segmentation** - Isolate services and environments
- **TLS Everywhere** - End-to-end encryption implementation
- **Access Control** - Authentication and authorization policies
- **Security Audits** - Comprehensive mesh security review

#### 🏗️ Infrastructure as Code
- **GitOps Implementation** - Automated deployment pipelines
- **Configuration Management** - Declarative infrastructure
- **CI/CD Integration** - Automated testing and deployment
- **Multi-Environment Setup** - Dev, staging, production workflows

#### 📊 High Availability & Performance
- **Multi-Node Clusters** - Redundancy and failover
- **Load Balancing** - Traffic distribution and optimization
- **Health Monitoring** - Automated health checks and recovery
- **Performance Tuning** - Optimization for high-traffic scenarios

#### 🛡️ Operations & Support
- **24/7 Monitoring** - Proactive issue detection
- **Incident Response** - Fast problem resolution
- **Capacity Planning** - Scaling strategies
- **Training & Documentation** - Knowledge transfer to your team

### Contact & Support

- 🌐 **Website**: [run-as-daemon.ru](https://run-as-daemon.ru)
- 🐙 **GitHub**: [@ranas-mukminov](https://github.com/ranas-mukminov)
- 💬 **Telegram/WhatsApp**: Available via website
- 📧 **Email**: Contact form on website

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/ranas-mukminov/cf-frp-traefik-mesh-wizard.git
cd cf-frp-traefik-mesh-wizard

# Install dependencies
pip install -e .[dev]

# Run formatting and linting
scripts/format.sh
scripts/lint.sh

# Run tests
pytest
```

## ⚖️ Legal & Responsible Use

Operate only on infrastructure you own or have authorization to manage. Respect the terms of Cloudflare, FRP, Traefik, and your hosting provider. This project automates legitimate configuration workflows and must not be used to bypass firewalls or violate acceptable use policies.

See [LEGAL.md](LEGAL.md) for more information.

## 📄 License

Apache License 2.0. See [LICENSE](LICENSE) for details.

---

## 🌍 Русская версия

Полная документация на русском языке доступна в [README.ru.md](README.ru.md)

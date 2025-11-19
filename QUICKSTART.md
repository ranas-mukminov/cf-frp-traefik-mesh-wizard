# ⚡ Quick Start Guide - cf-frp-traefik-mesh-wizard

Get your mesh network up and running in 5 minutes!

## 📋 Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.10 or higher installed
- ✅ A Cloudflare account with a domain
- ✅ A public VPS (e.g., Hetzner, DigitalOcean, AWS EC2)
- ✅ (Optional) A private LAN or homelab environment

## ⏱️ 5-Minute Setup

### Step 1: Install (1 minute)

Clone and install the wizard:

```bash
# Clone the repository
git clone https://github.com/ranas-mukminov/cf-frp-traefik-mesh-wizard.git
cd cf-frp-traefik-mesh-wizard

# Install in editable mode
pip install -e .

# Verify installation
mesh-wizard --help
```

### Step 2: Create Your Mesh Topology (2 minutes)

Choose one of these methods:

#### Option A: Use Interactive Wizard (Recommended for beginners)

```bash
mesh-wizard init
```

Follow the prompts to configure your mesh network.

#### Option B: Copy Example Template

```bash
# Copy the simple single VPS example
cp examples/simple-single-vps.yaml my-mesh.yaml

# Edit with your details
nano my-mesh.yaml  # or use your favorite editor
```

Update these values in `my-mesh.yaml`:
- `cloudflare.account_id` - Your Cloudflare account ID
- `cloudflare.tunnel_name` - Unique tunnel name
- `cloudflare.zone` - Your domain (e.g., `example.com`)
- `nodes[0].public_ip` - Your VPS public IP
- `frp.token` - Replace `CHANGE_ME_SECURE_TOKEN` with a strong random token

### Step 3: Validate & Generate (1 minute)

Validate your configuration:

```bash
mesh-wizard validate my-mesh.yaml
```

If validation passes, generate deployment configs:

```bash
mesh-wizard render my-mesh.yaml --out ./out
```

This creates:
```
out/
├── cloudflared/
│   └── config.yaml
├── frp/
│   ├── frps.toml
│   └── frpc.toml
└── traefik/
    ├── traefik.yaml
    └── dynamic/
        └── routers.yaml
```

### Step 4: Deploy (1 minute)

Copy generated configs to your nodes:

```bash
# On your VPS
scp -r out/cloudflared root@your-vps:/etc/cloudflared/
scp -r out/frp/frps.toml root@your-vps:/etc/frp/
scp -r out/traefik root@your-vps:/etc/traefik/

# Start services (example with systemd)
systemctl enable --now cloudflared
systemctl enable --now frps
systemctl enable --now traefik
```

🎉 **Congratulations!** Your mesh network is now running!

## 🎯 Common Use Cases

### 1. Home Lab with Cloudflare Tunnel

**Scenario**: Expose home services securely without opening ports.

```yaml
mesh:
  name: homelab
  description: Home services via Cloudflare Tunnel

cloudflare:
  tunnel_name: homelab-tunnel
  zone: myhome.example.com
  dns:
    - hostname: services.myhome.example.com
      target: service://homelab-router

nodes:
  - id: home-server
    role: lan_node
    frp:
      client: true
      server_addr: vps.example.com
      server_port: 7000
```

**Use this for**: Plex, Home Assistant, NAS access, etc.

### 2. Multi-Site VPN Mesh

**Scenario**: Connect multiple offices or data centers.

```yaml
mesh:
  name: multi-site-vpn
  description: Corporate multi-site mesh

nodes:
  - id: hq-vps
    role: public_vps
    location: us-east
    frp:
      server: true
  
  - id: office-london
    role: lan_node
    location: uk-london
    frp:
      client: true
  
  - id: office-tokyo
    role: lan_node
    location: jp-tokyo
    frp:
      client: true
```

**Use this for**: Branch office connectivity, hybrid cloud, disaster recovery.

### 3. Kubernetes Ingress with FRP

**Scenario**: Expose K3s/K8s cluster behind NAT.

```yaml
nodes:
  - id: k3s-cluster
    role: k8s_cluster
    frp:
      client: true
    traefik:
      enabled: true
      kubernetes: true

services:
  - id: k8s-ingress
    type: http
    node: k3s-cluster
    via: traefik
    router:
      rule: "Host(`app.example.com`)"
      service: kubernetes-service
```

**Use this for**: Homelab K3s, edge Kubernetes, IoT gateways.

### 4. Edge Proxy with Traefik

**Scenario**: Public-facing reverse proxy with dynamic routing.

```yaml
nodes:
  - id: edge-proxy
    role: public_vps
    traefik:
      enabled: true
      entrypoints:
        - name: websecure
          port: 443
      certificatesResolvers:
        letsencrypt:
          acme:
            email: admin@example.com
```

**Use this for**: Microservices, multi-tenant SaaS, API gateway.

## 🔍 Troubleshooting Quick Reference

### Issue: Validation fails with schema error

**Solution**: Check your YAML syntax and ensure all required fields are present.

```bash
# Detailed validation output
mesh-wizard validate my-mesh.yaml --verbose
```

### Issue: Cloudflare tunnel not connecting

**Checks**:
1. Verify `account_id` is correct (found in Cloudflare dashboard)
2. Ensure `tunnel_name` is unique
3. Check tunnel credentials are generated: `cloudflared tunnel create <name>`

```bash
# Test tunnel locally
cloudflared tunnel --config out/cloudflared/config.yaml run
```

### Issue: FRP connection refused

**Checks**:
1. Verify VPS firewall allows port 7000 (or your custom FRP bind_port)
2. Ensure `frp.token` matches on server and client
3. Check FRP server is running: `systemctl status frps`

```bash
# Test FRP server
frps -c out/frp/frps.toml

# Test FRP client with verbose logging
frpc -c out/frp/frpc.toml --log_level=debug
```

### Issue: Traefik 404 errors

**Checks**:
1. Verify router rules match your hostname
2. Check backend service is accessible
3. Review Traefik logs: `journalctl -u traefik -f`

```bash
# Check Traefik dashboard (if enabled)
curl http://localhost:8080/api/http/routers
```

### Issue: TLS certificate errors

**Solutions**:
- For Let's Encrypt: Ensure port 80/443 are accessible
- For Cloudflare Origin CA: Use Cloudflare SSL mode "Full (strict)"
- Check certificate resolver configuration in Traefik

## 📚 Next Steps

### Learn More

- 📖 **[Full README](README.md)** - Complete documentation
- 🚀 **[Deployment Guide](DEPLOYMENT.md)** - Production deployment best practices
- 🔒 **[Security Policy](SECURITY.md)** - Secure your mesh network
- 💡 **[Examples](examples/)** - More complex topologies

### Advanced Features

```bash
# AI-powered topology suggestions (requires OpenAI API key)
mesh-wizard ai-suggest "I need a HA setup with 2 VPS nodes"

# Generate HA/failover variants
mesh-wizard ai-ha my-mesh.yaml --out my-mesh-ha.yaml

# View ASCII network diagram
mesh-wizard diagram my-mesh.yaml
```

### Testing Your Setup

```bash
# Verify all services are accessible
curl https://your-domain.example.com

# Check health endpoints
curl https://your-domain.example.com/health

# Monitor logs
journalctl -f -u cloudflared -u frps -u traefik
```

## 🆘 Need Professional Help?

If you're stuck or need production-grade setup:

🌐 **[run-as-daemon.ru](https://run-as-daemon.ru)** - Professional Services

We offer:
- ✅ Custom mesh architecture design
- ✅ Production deployment assistance
- ✅ Security audits and hardening
- ✅ High-availability configuration
- ✅ 24/7 monitoring and support
- ✅ Training and knowledge transfer

💬 **Contact**: Visit [run-as-daemon.ru](https://run-as-daemon.ru) for Telegram/WhatsApp/Email

---

_Defense by design. Speed by default._

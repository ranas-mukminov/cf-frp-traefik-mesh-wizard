# 📖 Deployment Guide - cf-frp-traefik-mesh-wizard

Comprehensive guide for deploying production-grade mesh networks with Cloudflare Tunnel, FRP, and Traefik.

## 📋 Table of Contents

- [Understanding Mesh Architecture](#understanding-mesh-architecture)
- [Prerequisites](#prerequisites)
- [Step-by-Step Deployment](#step-by-step-deployment)
- [Production Deployment Best Practices](#production-deployment-best-practices)
- [High-Availability Setup](#high-availability-setup)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Professional Deployment Services](#professional-deployment-services)

## 🏗️ Understanding Mesh Architecture

### Architecture Layers

Your mesh network consists of multiple interconnected layers:

```
┌──────────────────────────────────────────────────────┐
│  Layer 1: Edge Ingress (Cloudflare)                  │
│  - Global CDN and DDoS protection                    │
│  - DNS and SSL/TLS termination                       │
│  - Cloudflare Access policies                        │
└──────────────────────┬───────────────────────────────┘
                       │ Encrypted Tunnel
┌──────────────────────▼───────────────────────────────┐
│  Layer 2: Public Gateway (VPS + Traefik)             │
│  - Reverse proxy and routing                         │
│  - TLS termination (optional)                        │
│  - Middleware (auth, rate limiting, etc.)            │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│  Layer 3: Tunnel Layer (FRP)                         │
│  - Fast Reverse Proxy tunneling                      │
│  - NAT traversal                                     │
│  - Token authentication                              │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│  Layer 4: Backend Services                           │
│  - K3s/K8s clusters                                  │
│  - Docker containers                                 │
│  - Bare metal applications                           │
└──────────────────────────────────────────────────────┘
```

### Traffic Flow

1. **Client Request** → Cloudflare Edge
2. **Cloudflare** → Cloudflare Tunnel → VPS
3. **VPS Traefik** → Routes based on hostname/path
4. **FRP Tunnel** → Forwards to private LAN
5. **Backend Service** → Processes request
6. **Response** → Flows back through same path

## ✅ Prerequisites

### System Requirements

#### VPS Node (Public Gateway)
- **OS**: Ubuntu 22.04 LTS or Debian 12 (recommended)
- **CPU**: 2+ cores
- **RAM**: 2GB+ (4GB recommended for production)
- **Storage**: 20GB+ SSD
- **Network**: Public IPv4 address, 1Gbps+ recommended

#### LAN/Homelab Node (Private)
- **OS**: Any Linux distribution, Windows (with WSL), or macOS
- **CPU**: 1+ core
- **RAM**: 1GB+
- **Storage**: 10GB+
- **Network**: Stable internet connection (upload speed matters)

### Software Requirements

- **Python 3.10+** (for mesh-wizard)
- **cloudflared** (Cloudflare Tunnel daemon)
- **frp** (Fast Reverse Proxy - server and/or client)
- **Traefik v2.10+** (reverse proxy)
- **Docker** (optional, for containerized deployments)

### Accounts & Credentials

- ✅ **Cloudflare Account** with:
  - Active zone (domain)
  - API token with Tunnel permissions
  - Account ID
- ✅ **VPS Provider Account** (Hetzner, DigitalOcean, AWS, etc.)
- ✅ **Domain Name** managed by Cloudflare

## 🚀 Step-by-Step Deployment

### 1. Cloudflare Tunnel Setup

#### 1.1 Create Cloudflare Tunnel

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Authenticate with Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create my-mesh-tunnel

# Note the Tunnel ID and credentials file location
```

#### 1.2 Configure Mesh YAML

```yaml
cloudflare:
  account_id: "your-account-id-here"
  tunnel_name: "my-mesh-tunnel"
  tunnel_id: "generated-tunnel-id"
  zone: "example.com"
  dns:
    - hostname: "*.example.com"
      entrypoint: websecure
      target: "service://traefik-router"
```

#### 1.3 Generate Config

```bash
mesh-wizard render mesh.yaml --out ./deployment
```

#### 1.4 Deploy Cloudflared

```bash
# Copy config to VPS
scp -r deployment/cloudflared root@your-vps:/etc/cloudflared/

# On VPS: Create systemd service
cat > /etc/systemd/system/cloudflared.service <<EOF
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/cloudflared tunnel --config /etc/cloudflared/config.yaml run
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl enable cloudflared
systemctl start cloudflared
systemctl status cloudflared
```

### 2. FRP Server Configuration

#### 2.1 Install FRP Server

```bash
# On VPS
FRP_VERSION="0.52.3"
wget https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/frp_${FRP_VERSION}_linux_amd64.tar.gz
tar -xzf frp_${FRP_VERSION}_linux_amd64.tar.gz
cp frp_${FRP_VERSION}_linux_amd64/frps /usr/local/bin/
```

#### 2.2 Deploy FRP Server Config

```bash
# Copy generated config
mkdir -p /etc/frp
cp deployment/frp/frps.toml /etc/frp/

# Create systemd service
cat > /etc/systemd/system/frps.service <<EOF
[Unit]
Description=FRP Server
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/frps -c /etc/frp/frps.toml
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl enable frps
systemctl start frps
systemctl status frps
```

#### 2.3 Configure Firewall

```bash
# Allow FRP bind port (default 7000)
ufw allow 7000/tcp

# Allow FRP vhost ports (if using HTTP/HTTPS vhosts)
ufw allow 19080/tcp
ufw allow 19443/tcp
```

### 3. FRP Client Setup

#### 3.1 Install FRP Client

```bash
# On LAN/homelab node
FRP_VERSION="0.52.3"
wget https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/frp_${FRP_VERSION}_linux_amd64.tar.gz
tar -xzf frp_${FRP_VERSION}_linux_amd64.tar.gz
cp frp_${FRP_VERSION}_linux_amd64/frpc /usr/local/bin/
```

#### 3.2 Deploy FRP Client Config

```bash
mkdir -p /etc/frp
cp deployment/frp/frpc.toml /etc/frp/

# Create systemd service
cat > /etc/systemd/system/frpc.service <<EOF
[Unit]
Description=FRP Client
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/frpc -c /etc/frp/frpc.toml
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl enable frpc
systemctl start frpc
systemctl status frpc
```

### 4. Traefik Deployment

#### 4.1 Install Traefik

```bash
# On VPS
TRAEFIK_VERSION="v2.10.5"
wget https://github.com/traefik/traefik/releases/download/${TRAEFIK_VERSION}/traefik_${TRAEFIK_VERSION}_linux_amd64.tar.gz
tar -xzf traefik_${TRAEFIK_VERSION}_linux_amd64.tar.gz
cp traefik /usr/local/bin/
```

#### 4.2 Deploy Traefik Config

```bash
mkdir -p /etc/traefik/dynamic
cp deployment/traefik/traefik.yaml /etc/traefik/
cp deployment/traefik/dynamic/* /etc/traefik/dynamic/

# Create systemd service
cat > /etc/systemd/system/traefik.service <<EOF
[Unit]
Description=Traefik
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/traefik --configFile=/etc/traefik/traefik.yaml
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl enable traefik
systemctl start traefik
systemctl status traefik
```

#### 4.3 Configure Firewall for Traefik

```bash
# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Optional: Traefik dashboard (secure with auth!)
ufw allow 8080/tcp
```

### 5. Validation & Testing

#### 5.1 Check All Services

```bash
# On VPS
systemctl status cloudflared frps traefik

# Check logs
journalctl -u cloudflared -f
journalctl -u frps -f
journalctl -u traefik -f

# On LAN node
systemctl status frpc
journalctl -u frpc -f
```

#### 5.2 Test Connectivity

```bash
# Test FRP tunnel
frpc -c /etc/frp/frpc.toml --log_level=debug

# Test Traefik routing
curl -H "Host: your-app.example.com" http://localhost

# Test end-to-end
curl https://your-app.example.com
```

#### 5.3 Verify DNS

```bash
# Check DNS resolution
dig your-app.example.com

# Should resolve to Cloudflare IPs
nslookup your-app.example.com
```

## 🏆 Production Deployment Best Practices

### Security Hardening

1. **Use Strong Tokens**
   ```bash
   # Generate secure FRP token
   openssl rand -base64 32
   ```

2. **Enable TLS Everywhere**
   - Cloudflare SSL mode: "Full (strict)"
   - FRP with TLS encryption
   - Traefik with automatic HTTPS redirect

3. **Implement Cloudflare Access**
   ```yaml
   cloudflare:
     access_policies:
       - name: "Admin Access"
         hostnames: ["admin.example.com"]
         require:
           - email: ["admin@example.com"]
   ```

4. **Firewall Rules**
   ```bash
   # Lock down VPS
   ufw default deny incoming
   ufw default allow outgoing
   ufw allow ssh
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw allow 7000/tcp  # FRP only
   ufw enable
   ```

### Performance Optimization

1. **Enable HTTP/2 and HTTP/3**
   ```yaml
   # In Traefik config
   experimental:
     http3: true
   ```

2. **Configure Connection Pooling**
   ```toml
   # In FRP config
   [common]
   pool_count = 5
   ```

3. **Use Compression**
   ```yaml
   # Traefik middleware
   compress:
     excludedContentTypes:
       - "text/event-stream"
   ```

### Monitoring Setup

1. **Prometheus Metrics**
   ```yaml
   # Traefik
   metrics:
     prometheus:
       addEntryPointsLabels: true
       addServicesLabels: true
   ```

2. **Health Checks**
   ```yaml
   services:
     - healthCheck:
         path: /health
         interval: 30s
         timeout: 5s
   ```

## 🔄 High-Availability Setup

### Multi-Node FRP Cluster

```yaml
nodes:
  - id: frp-primary
    role: public_vps
    location: us-east-1
    frp:
      server: true
      bind_port: 7000
  
  - id: frp-secondary
    role: public_vps
    location: us-west-1
    frp:
      server: true
      bind_port: 7000

# FRP clients with failover
frp:
  client:
    servers:
      - addr: frp-primary.example.com
        port: 7000
      - addr: frp-secondary.example.com
        port: 7000
```

### Traefik Clustering

```yaml
traefik:
  providers:
    consulCatalog:
      exposedByDefault: false
  
  # Use KV store for shared config
  consul:
    endpoints:
      - "consul-1.example.com:8500"
      - "consul-2.example.com:8500"
```

### Load Balancer Setup

```yaml
services:
  - id: app-lb
    type: http
    loadBalancer:
      servers:
        - url: "http://backend-1:8080"
        - url: "http://backend-2:8080"
      healthCheck:
        path: /health
        interval: 10s
```

## 📊 Monitoring & Logging

### Centralized Logging

#### With Loki + Promtail

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: varlogs
          __path__: /var/log/*log
  
  - job_name: traefik
    static_configs:
      - targets:
          - localhost
        labels:
          job: traefik
          __path__: /var/log/traefik/*.log
```

#### With ELK Stack

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/traefik/*.log
      - /var/log/cloudflared/*.log
      - /var/log/frp/*.log
    
output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "mesh-logs-%{+yyyy.MM.dd}"
```

### Metrics Collection

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'traefik'
    static_configs:
      - targets: ['localhost:8080']
  
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
  
  - job_name: 'frp'
    static_configs:
      - targets: ['localhost:7500']  # FRP dashboard port
```

### Alerting

```yaml
# alertmanager-config.yml
route:
  receiver: 'team-notifications'
  group_by: ['alertname', 'cluster']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: 'team-notifications'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK'
        channel: '#alerts'
        title: 'Mesh Network Alert'
```

## 💾 Backup & Recovery

### Configuration Backup

```bash
#!/bin/bash
# backup-configs.sh

BACKUP_DIR="/backup/mesh-configs-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup configs
cp -r /etc/cloudflared "$BACKUP_DIR/"
cp -r /etc/frp "$BACKUP_DIR/"
cp -r /etc/traefik "$BACKUP_DIR/"

# Backup mesh YAML
cp ~/mesh.yaml "$BACKUP_DIR/"

# Create tarball
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR.tar.gz" s3://my-backup-bucket/mesh/
```

### Disaster Recovery Procedure

1. **Document Your Setup**
   - Keep mesh YAML in version control (Git)
   - Document external dependencies
   - Maintain runbook for recovery

2. **Test Recovery Regularly**
   ```bash
   # Test restoration on staging
   ./restore-configs.sh backup-20240101.tar.gz
   systemctl restart cloudflared frps traefik
   ```

3. **Automate Backups**
   ```bash
   # Add to crontab
   0 2 * * * /usr/local/bin/backup-configs.sh
   ```

### State Management

- **Cloudflare Tunnel**: Credentials file (`<tunnel-id>.json`)
- **FRP**: No state (stateless proxy)
- **Traefik**: Configuration files + optional KV store
- **Let's Encrypt**: Certificate storage (`/etc/traefik/acme.json`)

## 🎓 Professional Deployment Services

### Need Expert Assistance?

🌐 **[run-as-daemon.ru](https://run-as-daemon.ru)** - _"Defense by design. Speed by default."_

We provide comprehensive deployment services:

#### 🚀 Deployment Packages

1. **Starter Deployment** ($$$)
   - Single VPS + LAN mesh setup
   - Basic security hardening
   - Documentation and training
   - 30-day support

2. **Production Deployment** ($$$$)
   - Multi-node HA setup
   - Advanced security (Zero-Trust)
   - Monitoring and alerting
   - Load balancing and failover
   - 90-day support

3. **Enterprise Deployment** ($$$$$)
   - Custom architecture design
   - Multi-region setup
   - 24/7 monitoring and support
   - Security audits and compliance
   - SLA guarantees
   - Ongoing managed services

#### 📞 Contact Us

- 🌐 **Website**: [run-as-daemon.ru](https://run-as-daemon.ru)
- 🐙 **GitHub**: [@ranas-mukminov](https://github.com/ranas-mukminov)
- 💬 **Telegram/WhatsApp**: Available via website
- 📧 **Email**: Contact form on website

---

**Ready to deploy?** Start with our [Quick Start Guide](QUICKSTART.md) or contact us for professional assistance!

_Defense by design. Speed by default._

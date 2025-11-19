# 🔒 Security Policy - cf-frp-traefik-mesh-wizard

## Reporting a Vulnerability

### How to Report

If you discover a security vulnerability in cf-frp-traefik-mesh-wizard, please report it responsibly:

1. **DO NOT** open a public GitHub issue
2. **DO NOT** disclose the vulnerability publicly until it has been addressed

**Report via**:
- 📧 **Email**: Contact through [run-as-daemon.ru](https://run-as-daemon.ru) contact form
- 🔒 **Private disclosure**: GitHub Security Advisories (preferred)
- 💬 **Direct message**: Via Telegram/WhatsApp through website

### What to Include

Please provide:
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (if available)
- Your contact information for follow-up

### Response Timeline

- **Initial Response**: Within 48 hours
- **Vulnerability Assessment**: Within 1 week
- **Fix Development**: Depends on severity (critical: days, high: weeks)
- **Public Disclosure**: After fix is released and users have time to update

### Recognition

We appreciate responsible disclosure and will:
- Credit you in the security advisory (unless you prefer to remain anonymous)
- Provide updates on the fix progress
- Notify you when the fix is released

## 🛡️ Security Best Practices

### Cloudflare Tunnel Security

#### Access Policies

Always implement Cloudflare Access policies for sensitive applications:

```yaml
cloudflare:
  access_policies:
    - name: "Admin Panel Access"
      hostnames:
        - "admin.example.com"
      require:
        - email:
            - "admin@example.com"
        - ip_range:
            - "203.0.113.0/24"  # Office IP range
    
    - name: "Team Access"
      hostnames:
        - "app.example.com"
      require:
        - email_domain:
            - "example.com"
```

#### Certificate Management

- ✅ Use Cloudflare Origin CA certificates for VPS
- ✅ Enable "Full (strict)" SSL mode in Cloudflare
- ✅ Rotate certificates before expiration
- ✅ Never commit certificates to version control

```bash
# Generate Origin CA certificate via Cloudflare Dashboard
# Install on VPS
cp origin-cert.pem /etc/ssl/certs/cloudflare-origin.pem
cp origin-key.pem /etc/ssl/private/cloudflare-origin.key
chmod 600 /etc/ssl/private/cloudflare-origin.key
```

#### Tunnel Authentication

- ✅ Store tunnel credentials securely
- ✅ Use unique tunnel per environment (dev/staging/prod)
- ✅ Regularly rotate tunnel credentials
- ✅ Implement least privilege access

### FRP Security

#### Token Authentication

**CRITICAL**: Always use strong, unique tokens for FRP authentication.

```toml
# frps.toml (server)
auth.method = "token"
auth.token = "REPLACE_WITH_SECURE_RANDOM_TOKEN"

# Generate secure token
# openssl rand -base64 32
```

```toml
# frpc.toml (client)
auth.method = "token"
auth.token = "SAME_SECURE_TOKEN_AS_SERVER"
```

⚠️ **Never**:
- Use default tokens like "CHANGE_ME"
- Commit tokens to version control
- Share tokens between environments
- Use weak or predictable tokens

#### TLS Encryption

Enable TLS for FRP connections:

```toml
# frps.toml
transport.tls.force = true
transport.tls.certFile = "/etc/frp/server.crt"
transport.tls.keyFile = "/etc/frp/server.key"

# frpc.toml
transport.tls.enable = true
transport.tls.serverName = "frp.example.com"
```

Generate self-signed certificate for FRP:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/frp/server.key \
  -out /etc/frp/server.crt \
  -subj "/CN=frp.example.com"
```

#### Network Segmentation

Isolate FRP services:

```bash
# Firewall rules - only allow specific ports
ufw default deny incoming
ufw allow from 203.0.113.0/24 to any port 7000  # FRP bind port, trusted IPs only
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

#### Connection Limits

Prevent abuse with connection limits:

```toml
# frps.toml
transport.maxPoolCount = 50
maxPortsPerClient = 10
```

### Traefik Security

#### TLS Termination

Configure strong TLS settings:

```yaml
# traefik.yaml
tls:
  options:
    default:
      minVersion: VersionTLS12
      cipherSuites:
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
        - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
      curvePreferences:
        - CurveP521
        - CurveP384
```

#### Authentication Middleware

Protect sensitive endpoints:

```yaml
# Basic Auth
http:
  middlewares:
    admin-auth:
      basicAuth:
        users:
          - "admin:$apr1$H6uskkkW$IgXLP6ewTrSuBkTrqE8wj/"  # admin:secure_password
        removeHeader: true

# OAuth/OIDC
    oauth-auth:
      forwardAuth:
        address: "https://auth.example.com/verify"
        trustForwardHeader: true
```

Generate basic auth password:

```bash
htpasswd -nb admin secure_password
# or
echo $(htpasswd -nb admin secure_password) | sed -e s/\\$/\\$\\$/g
```

#### Security Headers

Add security headers middleware:

```yaml
http:
  middlewares:
    security-headers:
      headers:
        accessControlAllowMethods:
          - GET
          - OPTIONS
          - PUT
          - POST
          - DELETE
        accessControlMaxAge: 100
        addVaryHeader: true
        sslRedirect: true
        stsSeconds: 31536000
        stsIncludeSubdomains: true
        stsPreload: true
        forceSTSHeader: true
        frameDeny: true
        contentTypeNosniff: true
        browserXssFilter: true
        referrerPolicy: "strict-origin-when-cross-origin"
        customResponseHeaders:
          X-Robots-Tag: "none,noarchive,nosnippet,notranslate,noimageindex"
          X-Frame-Options: "DENY"
          X-Content-Type-Options: "nosniff"
```

#### Rate Limiting

Protect against abuse:

```yaml
http:
  middlewares:
    rate-limit:
      rateLimit:
        average: 100
        burst: 50
        period: 1m
```

## 🔐 Secret Management

### Never Commit Secrets

**Add to `.gitignore`**:

```gitignore
# Secrets
*.secret.*
*-secret.*
secrets/
.env
.env.local

# Credentials
*.key
*.pem
*.crt
credentials.json
*-credentials.json

# Cloudflare
*tunnel-credentials.json

# FRP tokens
frps-token.txt
frpc-token.txt
```

### Use Environment Variables

```bash
# .env (never commit!)
CLOUDFLARE_ACCOUNT_ID="abc123..."
CLOUDFLARE_TUNNEL_ID="def456..."
FRP_AUTH_TOKEN="ghi789..."
TRAEFIK_ADMIN_PASSWORD="jkl012..."
```

Load in configs:

```yaml
cloudflare:
  account_id: ${CLOUDFLARE_ACCOUNT_ID}
  tunnel_id: ${CLOUDFLARE_TUNNEL_ID}
```

### Vault Integration

For production, use HashiCorp Vault:

```bash
# Store secrets in Vault
vault kv put secret/mesh/cloudflare \
  account_id="abc123..." \
  tunnel_id="def456..."

vault kv put secret/mesh/frp \
  auth_token="secure-random-token"

# Retrieve in deployment scripts
export FRP_TOKEN=$(vault kv get -field=auth_token secret/mesh/frp)
```

### Secret Rotation

Regularly rotate secrets:

1. **FRP Tokens**: Every 90 days
2. **Cloudflare API Tokens**: Every 180 days
3. **TLS Certificates**: Before expiration (auto-renewed with Let's Encrypt)
4. **Admin Passwords**: Every 90 days

## 🌐 Network Security

### Firewall Rules

#### VPS (Public Gateway)

```bash
#!/bin/bash
# firewall-setup.sh

# Reset rules
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# SSH (restrict to trusted IPs)
ufw allow from 203.0.113.0/24 to any port 22

# HTTP/HTTPS (public)
ufw allow 80/tcp
ufw allow 443/tcp

# FRP (restrict to known clients)
ufw allow from 198.51.100.0/24 to any port 7000

# Cloudflare IPs only for direct connections (optional)
# https://www.cloudflare.com/ips/
for ip in $(curl -s https://www.cloudflare.com/ips-v4); do
  ufw allow from $ip to any port 80
  ufw allow from $ip to any port 443
done

# Enable firewall
ufw --force enable
ufw status verbose
```

#### LAN/Homelab Node

```bash
# More permissive for internal network
ufw default allow outgoing
ufw default deny incoming
ufw allow from 192.168.1.0/24  # Local network
ufw allow from YOUR_VPS_IP to any port 22  # SSH from VPS
ufw enable
```

### Zero-Trust Principles

Implement defense-in-depth:

1. **Perimeter Security** - Cloudflare WAF and DDoS protection
2. **Transport Security** - TLS/SSL everywhere
3. **Authentication** - Cloudflare Access, Traefik auth middleware
4. **Authorization** - Fine-grained access control
5. **Network Segmentation** - Isolated network zones
6. **Monitoring** - Log all access attempts

### Least Privilege Access

```yaml
# Example: Restricted access by IP and email
cloudflare:
  access_policies:
    - name: "Production Admin"
      require:
        - email: ["admin@example.com"]
        - ip_range: ["203.0.113.0/24"]
        - country: ["US"]
      decision: allow
    
    - name: "Deny All Others"
      require:
        - everyone: true
      decision: deny
```

## 📋 Audit & Compliance

### Logging Configuration

Enable comprehensive logging:

```yaml
# Traefik
accessLog:
  filePath: "/var/log/traefik/access.log"
  format: json
  fields:
    headers:
      defaultMode: keep
      names:
        User-Agent: keep
        Authorization: drop
        X-Forwarded-For: keep

log:
  level: INFO
  filePath: "/var/log/traefik/traefik.log"
  format: json
```

```toml
# FRP Server
[common]
log_file = "/var/log/frp/frps.log"
log_level = "info"
log_max_days = 30
```

### Access Monitoring

Monitor for suspicious activity:

```bash
# Watch for failed auth attempts
tail -f /var/log/auth.log | grep "Failed password"

# Monitor Traefik access logs
tail -f /var/log/traefik/access.log | jq '.ClientHost, .RequestPath, .DownstreamStatus'

# FRP connection logs
journalctl -u frps -f | grep "login"
```

### Regular Security Reviews

Perform quarterly reviews:

- [ ] Audit user access and permissions
- [ ] Review firewall rules
- [ ] Check for outdated software versions
- [ ] Scan for exposed secrets in git history
- [ ] Test disaster recovery procedures
- [ ] Verify backup integrity
- [ ] Update security documentation

### Compliance Considerations

For regulated industries:

- **GDPR**: Log data retention, encryption at rest
- **HIPAA**: Audit trails, access controls
- **PCI-DSS**: Network segmentation, encryption
- **SOC 2**: Monitoring, incident response

## 🚨 Incident Response

### Detection

Monitor for:
- Unusual traffic patterns
- Failed authentication attempts
- Unauthorized configuration changes
- Suspicious log entries

### Response Procedure

1. **Contain**: Isolate affected systems
2. **Investigate**: Analyze logs and determine scope
3. **Eradicate**: Remove threat, patch vulnerabilities
4. **Recover**: Restore from clean backups
5. **Document**: Record incident details
6. **Review**: Post-incident analysis and improvements

### Emergency Contacts

Maintain contact list:
- Security team lead
- Infrastructure admin
- Cloudflare support
- VPS provider support
- Legal/compliance team

## 🎓 Professional Security Audit

### Comprehensive Security Assessment

🌐 **[run-as-daemon.ru](https://run-as-daemon.ru)** offers professional security audits:

#### What's Included

✅ **Configuration Review**
- Mesh topology analysis
- Cloudflare security settings
- FRP authentication and encryption
- Traefik security headers and middleware

✅ **Vulnerability Assessment**
- Network scanning
- Dependency analysis
- Common misconfiguration checks
- Penetration testing (optional)

✅ **Compliance Check**
- Industry standards alignment
- Best practices validation
- Documentation review

✅ **Recommendations Report**
- Prioritized findings
- Remediation steps
- Implementation guidance

#### Pricing

- **Basic Audit**: Configuration review and recommendations
- **Comprehensive Audit**: Full assessment with vulnerability scanning
- **Continuous Monitoring**: Ongoing security monitoring and alerts

#### Contact for Security Services

- 🌐 **Website**: [run-as-daemon.ru](https://run-as-daemon.ru)
- 🔒 **Secure Contact**: Via website encrypted form
- 💬 **Consultation**: Free initial security consultation

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Cloudflare Security Documentation](https://developers.cloudflare.com/security/)
- [Traefik Security Best Practices](https://doc.traefik.io/traefik/https/overview/)
- [FRP Security Configuration](https://github.com/fatedier/frp#security)

---

_Defense by design. Speed by default._

**Last Updated**: 2024-01-19

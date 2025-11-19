# Contributing

Thank you for helping `cf-frp-traefik-mesh-wizard` evolve. This project targets production-ready DevSecOps workflows, so every contribution must keep security and documentation front of mind.

## Ways to contribute
- Fix bugs in generators, schema, CLI, or docs.
- Extend schema with new mesh patterns together with examples/tests.
- Improve CI, linting, and security/performance checks.

## Development setup
1. Install Python 3.10+.
2. Clone the repo and install dependencies:
   ```bash
   pip install -e .[dev]
   ```
3. Run formatting/linting before committing:
   ```bash
   scripts/format.sh
   scripts/lint.sh
   ```
4. Run the full test suite (unit + integration):
   ```bash
   pytest
   ```
5. When touching security-sensitive code (AI helpers, generators), run:
   ```bash
   scripts/security_scan.sh
   scripts/perf_check.sh   # optional but recommended before releases
   ```

## Pull request checklist
- Reference related issues or topology requirements.
- Update `README.md`, `schema/mesh-schema.yaml`, and `examples/` if semantics change.
- Include tests for new behavior and ensure CI is green.
- Avoid committing secrets; keep FRP tokens and Cloudflare credentials as placeholders.

## Code style
- Python formatted with `black`/`isort`, linted with `ruff`.
- YAML uses two-space indents with trailing newline (enforced by `.editorconfig`).
- Prefer small, typed functions and docstrings describing intent rather than implementation details.

## Communication

Open a GitHub issue for significant changes before implementing them. 

### Community Support

For general questions and discussions:
- 🐙 **GitHub Issues**: For bug reports and feature requests
- 💬 **GitHub Discussions**: For questions and community help

### Professional Support & Consulting

For production deployments, custom implementations, or professional consulting:

🌐 **[run-as-daemon.ru](https://run-as-daemon.ru)** - _"Defense by design. Speed by default."_

Professional services:
- 🏗️ **Custom Architecture Design** - Tailored mesh network solutions
- 🔒 **Security Consulting** - Audits, hardening, and compliance
- 📊 **Production Deployments** - High-availability, zero-trust implementations
- 🤖 **Automation & CI/CD** - Infrastructure as Code and GitOps
- 🎓 **Training & Workshops** - Team training and knowledge transfer
- 🛡️ **Managed Services** - Ongoing support and monitoring

**Contact**:
- 🌐 Website: [run-as-daemon.ru](https://run-as-daemon.ru)
- 🐙 GitHub: [@ranas-mukminov](https://github.com/ranas-mukminov)
- 💬 Telegram/WhatsApp: Available via website
- 📧 Email: Contact form on website

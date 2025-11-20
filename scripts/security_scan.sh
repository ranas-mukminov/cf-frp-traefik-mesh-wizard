#!/usr/bin/env bash
set -euo pipefail

# Generate a requirements file from project dependencies only
# This excludes system packages that aren't part of the project
pip list --format=freeze | grep -E "^(PyYAML|jsonschema|typer|rich|openai|pytest|pytest-cov|ruff|black|isort|yamllint|bandit|pip-audit)" > /tmp/project_deps.txt

# Only audit project dependencies, not system packages
pip-audit --requirement /tmp/project_deps.txt

# Run bandit security scan on source code
bandit -r src

#!/usr/bin/env bash
set -euo pipefail

black src tests
isort src tests

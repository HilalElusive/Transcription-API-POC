#!/usr/bin/env bash
set -euo pipefail

ansible app -i inventory.ini -b -m shell \
  -a "echo '${CI_REGISTRY_PASSWORD}' | docker login -u '${CI_REGISTRY_USER}' --password-stdin '${CI_REGISTRY}'"
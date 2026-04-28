# Kubernetes manifests

Applied in alphabetical order by `kubectl apply -f manifests/`. Numeric
prefixes enforce ordering:

- `00-namespace.yaml` — creates the `transcription` namespace
- `10-secrets.yaml.j2` — Ansible template, rendered to `10-secrets.yaml`
  before apply; provides app-secrets (OpenAI + DB) and gitlab-registry
  (image pull credentials)
- `20-postgres.yaml` — Postgres StatefulSet with PVC and headless Service
- `30-api.yaml.j2` — Ansible template (image tag is variable);
  Deployment with 2 replicas + NodePort Service on port 30080

Re-running the playbook is safe — `kubectl apply` is idempotent.
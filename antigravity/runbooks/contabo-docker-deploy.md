# Contabo VPS Docker Deployment Runbook

1. Provision Ubuntu LTS VPS.
2. Install Docker and Docker Compose plugin.
3. Add deploy SSH key.
4. Clone GitHub repository.
5. Copy `.env` with production values.
6. Run:

```bash
docker compose -f docker/docker-compose.prod.yml up -d --build
```

7. Verify:

```bash
docker compose -f docker/docker-compose.prod.yml logs -f controller
```

Do not store secrets in Git.

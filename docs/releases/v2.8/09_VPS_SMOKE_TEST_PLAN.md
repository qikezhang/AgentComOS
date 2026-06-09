# 09 VPS Smoke Test Plan

## Goal

Validate v2.8 final delivery on VPS using Docker Compose, Real Discord Bot, and Controlled Executor.

## Smoke sequence

1. Clone repository.
2. Checkout release candidate.
3. Prepare `.env` from `.env.example`.
4. Start Docker Compose.
5. Verify healthcheck.
6. Run G0-G11 smoke.
7. Connect Real Discord Bot.
8. Send read-only Discord status command.
9. Send controlled docker logs command.
10. Send blocked arbitrary shell command.
11. Send allowlisted systemctl status command.
12. Send permission-conflict command.
13. Send blocked secret request.
14. Generate Evidence / Delivery / GM Report.
15. Verify backup/restore path.
16. Verify no secrets in repo.
17. Clean runtime artifacts or keep them in external volume only.

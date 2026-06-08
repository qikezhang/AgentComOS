.PHONY: test validate-examples doctor compile cli-help local-up local-down package

test:
	./.venv/bin/pytest -q

compile:
	./.venv/bin/python3 -m compileall src tests

cli-help:
	PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli --help >/dev/null

validate-examples:
	PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli validate examples/techai8/run/OI-TECHAI8-001

doctor:
	PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli doctor

local-up:
	docker compose -f docker/docker-compose.local.yml up -d

local-down:
	docker compose -f docker/docker-compose.local.yml down

package:
	./.venv/bin/python3 scripts/package.py

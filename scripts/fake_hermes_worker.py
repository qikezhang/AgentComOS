#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agentcomos.worker.fake_hermes import write_fake_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic fake Hermes worker for G4.")
    parser.add_argument("--invocation", required=True, type=Path)
    args = parser.parse_args()

    result = write_fake_outputs(args.invocation)
    print(
        "Fake Hermes worker completed: "
        f"run_id={result['run_id']} task_id={result['task_id']} "
        f"output_dir={result['output_dir']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


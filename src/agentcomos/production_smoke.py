import os
import shutil
import json
import yaml
from pathlib import Path
from agentcomos.release_readiness import check_release_readiness

def run_production_smoke(runtime_dir: Path) -> dict:
    runtime_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    
    # Run healthcheck
    hc = os.popen("PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli healthcheck").read()
    results["healthcheck"] = "pass" if "status\": \"ok" in hc else "fail"
    
    # Discord status
    ds = os.popen("PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli discord status").read()
    results["discord_status"] = "pass" if "token_missing" in ds or "enabled: false" in ds else "fail"
    
    # Executor status
    es = os.popen("PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli executor status").read()
    results["executor_status"] = "pass" if "real_execution_available: false" in es else "fail"
    
    # Adapter status
    as_out = os.popen("PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli adapter status").read()
    results["adapter_status"] = "pass" if "real_execution_available: false" in as_out else "fail"
    
    # Adapter dry-run
    req_file = Path("tests/fixtures/adapters/systemctl_status_request.yaml")
    if req_file.exists():
        adr = os.popen(f"PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli adapter dry-run --request-file {req_file} --runtime-dir {runtime_dir}").read()
        results["adapter_dry_run"] = "pass" if "blocked" in adr or "executor_disabled" in adr else "fail"
    else:
        results["adapter_dry_run"] = "unavailable"
        
    # Docker compose config
    if shutil.which("docker"):
        dc = os.popen("docker compose config").read()
        results["docker_compose_config"] = "pass" if "services:" in dc else "fail"
    else:
        results["docker_compose_config"] = "unavailable"
        
    # No real execution fields check
    real_exec = False
    for f in runtime_dir.glob("*"):
        if f.is_file():
            content = f.read_text()
            if "real_execution: true" in content or "execution_mode: real" in content:
                real_exec = True
    results["real_execution_check"] = "fail" if real_exec else "pass"
    
    # Secret scan
    secret_found = False
    for f in runtime_dir.glob("*"):
        if f.is_file():
            content = f.read_text()
            if "DISCORD_BOT_TOKEN=" in content and "replace-with-deployment-secret" not in content:
                secret_found = True
            if "PRIVATE KEY" in content:
                secret_found = True
    results["secret_scan"] = "fail" if secret_found else "pass"
    
    overall_status = "pass"
    for k, v in results.items():
        if v == "fail":
            overall_status = "fail"
            break
            
    report = {
        "status": overall_status,
        "results": results
    }
    
    report_file = runtime_dir / "production_smoke_report.yaml"
    report_file.write_text(yaml.dump(report))
    
    return report

def evaluate_go_no_go(readiness_report: dict, smoke_report: dict) -> dict:
    reasons = []
    status = "go"
    
    if readiness_report.get("status") != "pass":
        status = "no_go"
        reasons.append("Readiness report failed")
        
    if smoke_report.get("status") != "pass":
        status = "no_go"
        reasons.append("Smoke report failed")
        
    for b in readiness_report.get("blockers", []):
        reasons.append(f"Blocker: {b}")
        status = "no_go"
        
    return {
        "status": status,
        "reasons": reasons
    }

def create_evidence_bundle(runtime_dir: Path) -> dict:
    runtime_dir.mkdir(parents=True, exist_ok=True)
    
    rr = check_release_readiness()
    (runtime_dir / "release_readiness_report.yaml").write_text(yaml.dump(rr))
    
    sr = run_production_smoke(runtime_dir)
    
    gng = evaluate_go_no_go(rr, sr)
    (runtime_dir / "go_no_go_report.yaml").write_text(yaml.dump(gng))
    
    # Collect git info
    try:
        git_branch = os.popen("git branch --show-current").read().strip()
        git_commit = os.popen("git log -1 --format=%H").read().strip()
    except Exception:
        git_branch = "unknown"
        git_commit = "unknown"
        
    manifest = {
        "git_branch": git_branch,
        "git_commit": git_commit,
        "readiness_status": rr.get("status"),
        "smoke_status": sr.get("status"),
        "go_no_go_status": gng.get("status")
    }
    
    (runtime_dir / "manifest.yaml").write_text(yaml.dump(manifest))
    
    return manifest

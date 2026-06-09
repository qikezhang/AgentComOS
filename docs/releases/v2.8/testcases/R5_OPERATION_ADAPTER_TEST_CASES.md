# R5 Operation Adapter Test Cases

## R5-ADP-001 Shell healthcheck
Input: `shell_allowed_healthcheck.yaml`.  
Expected: allowed, timeout enforced.

## R5-ADP-002 SSH status
Input: `ssh_allowed_remote_status.yaml`.  
Expected: allowed if host available, otherwise safe unavailable.  
Must not happen: arbitrary ssh session.

## R5-ADP-003 Sudo restart
Input: `sudo_allowed_service_restart.yaml`.  
Expected: allowed only if policy explicitly allows command_ref.

## R5-ADP-004 Docker logs
Input: `docker_allowed_logs.yaml`.  
Expected: logs returned redacted.

## R5-ADP-005 Systemctl status
Input: `systemctl_allowed_status.yaml`.  
Expected: service status returned.

## R5-ADP-006 Docker prune blocked
Input: `blocked_docker_prune.yaml`.  
Expected: blocked, not executed.

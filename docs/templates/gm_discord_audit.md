# GM Discord Audit

**Run ID:** {{ run_id }}

## Inbound Summary
- **Message ID:** {{ message_id }}
- **Received At:** {{ received_at }}
- **Content:** {{ content_redacted }}

## Parsed Command
- **Command ID:** {{ command_id }}
- **Command Type:** {{ command_type }}
- **Risk Level:** {{ risk_level }}
- **Confirmation Requirement:** {{ requires_confirmation }}

## Result Summary
- **Status:** {{ result_status }}
- **Summary:** {{ result_summary }}

## Safety Boundary
- Token Present: false
- Shell Executed: false
- Manual OS Bypassed: false
- Decision/Feynman Bypassed: false

## Evidence Paths
- Inbound Message: `{{ inbound_path }}`
- GM Command: `{{ command_path }}`
- GM Command Result: `{{ result_path }}`

## Next Action
{{ next_action }}

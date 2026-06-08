import pytest
import shutil
import yaml
from pathlib import Path
from agentcomos.controller.state import RunState, get_run_dir, read_run_status, write_run_status
from agentcomos.controller.runner import handle_run_create, handle_run_status, handle_controller_tick, handle_controller_recover
from agentcomos.controller.events import read_events

@pytest.fixture
def clean_run():
    run_id = "OI-TEST-123"
    run_dir = get_run_dir(run_id)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    
    # Create fake intent
    intent_path = Path(".agentcomos/tmp/test_intent.yaml")
    intent_path.parent.mkdir(parents=True, exist_ok=True)
    intent_path.write_text(f"run_id: {run_id}\n", encoding="utf-8")
    
    yield run_id, intent_path
    
    if run_dir.exists():
        shutil.rmtree(run_dir)

def test_run_status_is_read_only(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    
    run_dir = get_run_dir(run_id)
    status_file = run_dir / "run_status.yaml"
    events_file = run_dir / "events.jsonl"
    timeline_file = run_dir / "timeline.yaml"
    
    events_content_1 = events_file.read_text()
    timeline_content_1 = timeline_file.read_text()
    events_count_1 = len(read_events(run_id))
    
    handle_run_status(run_id)
    
    events_content_2 = events_file.read_text()
    timeline_content_2 = timeline_file.read_text()
    
    assert events_content_1 == events_content_2
    assert timeline_content_1 == timeline_content_2
    assert len(read_events(run_id)) == events_count_1

def test_fake_tick_path_includes_reported(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    
    for _ in range(15):
        handle_controller_tick(run_id, fake=True)
        status = read_run_status(run_id)
        if status["state"] == RunState.completed.value:
            break
            
    events = read_events(run_id)
    state_changes = [e["payload"]["to_state"] for e in events if e["type"] == "run.state_changed"]
    
    assert RunState.reported.value in state_changes
    assert RunState.completed.value in state_changes
    
    reported_idx = state_changes.index(RunState.reported.value)
    completed_idx = state_changes.index(RunState.completed.value)
    assert reported_idx < completed_idx

def test_completed_tick_is_idempotent(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    
    for _ in range(15):
        handle_controller_tick(run_id, fake=True)
        if read_run_status(run_id)["state"] == RunState.completed.value:
            break
            
    run_dir = get_run_dir(run_id)
    dp_file = run_dir / "delivery_packet.yaml"
    ep_file = run_dir / "evidence_packet" / "manifest.yaml"
    
    dp_content_1 = dp_file.read_text()
    ep_content_1 = ep_file.read_text()
    
    events_count_before = len([e for e in read_events(run_id) if e["type"] == "run.state_changed"])
    
    handle_controller_tick(run_id, fake=True)
    
    assert read_run_status(run_id)["state"] == RunState.completed.value
    assert dp_file.read_text() == dp_content_1
    assert ep_file.read_text() == ep_content_1
    
    events_count_after = len([e for e in read_events(run_id) if e["type"] == "run.state_changed"])
    assert events_count_before == events_count_after

def test_missing_intent_fails(clean_run):
    with pytest.raises(ValueError):
        handle_run_create(Path("non_existent_fake_path.yaml"))

def test_invalid_transition_fails_or_is_blocked(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    
    status = read_run_status(run_id)
    status["state"] = "nonsense_state"
    write_run_status(run_id, status)
    
    with pytest.raises(ValueError, match="Invalid state"):
        handle_controller_tick(run_id, fake=True)

def test_recover_does_not_delete_events(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    handle_controller_tick(run_id, fake=True)
    
    events_count_1 = len(read_events(run_id))
    
    handle_controller_recover(run_id)
    
    events_count_2 = len(read_events(run_id))
    assert events_count_2 >= events_count_1

def test_run_create_does_not_overwrite_existing_run(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    handle_controller_tick(run_id, fake=True)
    
    status_1 = read_run_status(run_id)
    events_count_1 = len(read_events(run_id))
    
    handle_run_create(intent_path)
    
    status_2 = read_run_status(run_id)
    events_count_2 = len(read_events(run_id))
    
    assert status_1["state"] == status_2["state"]
    assert events_count_1 == events_count_2

def test_run_create_generates_status(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    
    status = read_run_status(run_id)
    assert status is not None
    assert status["run_id"] == run_id
    assert status["state"] == RunState.created.value
    
    events = read_events(run_id)
    assert len(events) == 1
    assert events[0]["type"] == "run.created"
    assert "event_id" in events[0]
    assert "timestamp" in events[0]
    assert events[0]["actor"] == "controller"
    assert (get_run_dir(run_id) / "timeline.yaml").exists()

def test_status_raises_on_missing():
    with pytest.raises(ValueError):
        handle_run_status("non-existent-run")

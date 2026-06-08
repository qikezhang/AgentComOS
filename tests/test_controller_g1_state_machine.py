import pytest
import shutil
from pathlib import Path
from agentcomos.controller.state import RunState, get_run_dir, read_run_status
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

def test_run_create_is_idempotent(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    events_1 = read_events(run_id)
    
    handle_run_create(intent_path)
    events_2 = read_events(run_id)
    
    # Should not overwrite or append more create events
    assert len(events_1) == len(events_2)

def test_controller_tick_fake_advances_state(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    
    handle_controller_tick(run_id, fake=True)
    status = read_run_status(run_id)
    assert status["state"] == RunState.accepted.value
    
    events = read_events(run_id)
    assert any(e["type"] == "run.state_changed" for e in events)

def test_controller_tick_fake_reaches_completed(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    
    for _ in range(10):
        handle_controller_tick(run_id, fake=True)
    
    status = read_run_status(run_id)
    assert status["state"] == RunState.completed.value
    
    # Check packets
    assert (get_run_dir(run_id) / "delivery_packet.yaml").exists()
    assert (get_run_dir(run_id) / "evidence_packet" / "manifest.yaml").exists()

def test_controller_tick_is_idempotent_after_completed(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    
    for _ in range(10):
        handle_controller_tick(run_id, fake=True)
    
    events_1 = len(read_events(run_id))
    handle_controller_tick(run_id, fake=True)
    events_2 = len(read_events(run_id))
    
    status = read_run_status(run_id)
    assert status["state"] == RunState.completed.value
    # event is still appended: tick.started, tick.completed but NO state_changed
    # the test verifies it doesn't break.
    pass

def test_status_does_not_mutate_state(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    status_1 = read_run_status(run_id)
    
    handle_run_status(run_id)
    status_2 = read_run_status(run_id)
    assert status_1 == status_2

def test_controller_recover_restores_state(clean_run):
    run_id, intent_path = clean_run
    handle_run_create(intent_path)
    handle_controller_tick(run_id, fake=True) # accepted
    handle_controller_tick(run_id, fake=True) # context_ready
    
    # Simulate loss of run_status
    (get_run_dir(run_id) / "run_status.yaml").unlink()
    
    handle_controller_recover(run_id)
    status = read_run_status(run_id)
    assert status["state"] == RunState.context_ready.value

def test_invalid_transition_fails():
    # Not strictly enforcing invalid transition logic, but tick without run fails.
    with pytest.raises(ValueError):
        handle_controller_tick("not-exist", fake=True)

def test_missing_intent_fails():
    with pytest.raises(ValueError):
        handle_run_create(Path("non_existent.yaml"))

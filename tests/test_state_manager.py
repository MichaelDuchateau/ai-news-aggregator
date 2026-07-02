import json
from datetime import datetime, timedelta

from src.state_manager import StateManager


def test_get_current_week_year_boundary(tmp_path):
    state = StateManager(state_dir=str(tmp_path / "state"))
    assert state.get_current_week(now=datetime(2027, 1, 1)) == "2026-W53"
    assert state.get_current_week(now=datetime(2024, 12, 30)) == "2025-W01"


def test_prune_drops_old_entries_keeps_recent(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    now = datetime.now()
    old_entry = {
        "url": "https://old.example/1",
        "first_seen": (now - timedelta(weeks=20)).isoformat(),
        "status": "scanned",
        "week": "2025-W01",
    }
    recent_entry = {
        "url": "https://recent.example/1",
        "first_seen": (now - timedelta(weeks=1)).isoformat(),
        "status": "scanned",
        "week": "2026-W01",
    }
    (state_dir / "processed_urls.json").write_text(json.dumps({
        old_entry["url"]: old_entry,
        recent_entry["url"]: recent_entry,
    }))

    state = StateManager(state_dir=str(state_dir), prune_after_weeks=12)

    assert old_entry["url"] not in state.processed_urls
    assert recent_entry["url"] in state.processed_urls


def test_mark_and_is_url_processed_round_trip(tmp_path):
    state = StateManager(state_dir=str(tmp_path / "state"))

    url = "https://example.com/article"
    assert not state.is_url_processed(url)

    state.mark_url_processed(url, status="scanned", week="2026-W01")

    assert state.is_url_processed(url)

    # Reload from disk to confirm persistence.
    reloaded = StateManager(state_dir=str(tmp_path / "state"))
    assert reloaded.is_url_processed(url)
    assert reloaded.processed_urls[url].status == "scanned"
    assert reloaded.processed_urls[url].week == "2026-W01"

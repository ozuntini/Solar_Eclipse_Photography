import json
from datetime import time

from config.eclipse_config import ActionConfig
from utils.action_journal import ActionJournal


def _load_entries(path):
    with open(path, "r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def test_scheduled_at_resolved_for_relative_action(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    journal = ActionJournal(str(journal_path), test_mode=True)

    journal.log_circumstance(
        time(14, 41, 5),
        time(16, 2, 50),
        time(16, 3, 53),
        time(16, 4, 58),
        time(17, 31, 3),
    )

    action = ActionConfig(
        action_type="Photo",
        time_ref="C2",
        start_operator="+",
        start_time=time(0, 0, 10),
    )

    journal.log_action_start(action_index=0, action_config=action, next_action_config=None)
    journal.close()

    entries = _load_entries(journal_path)
    action_start_entry = next(item for item in entries if item["event"] == "ACTION_START")

    assert action_start_entry["current_action"]["scheduled_at"] == "16:03:00"


def test_scheduled_at_none_without_circumstance(tmp_path):
    journal_path = tmp_path / "journal.jsonl"
    journal = ActionJournal(str(journal_path), test_mode=True)

    action = ActionConfig(
        action_type="Photo",
        time_ref="C2",
        start_operator="+",
        start_time=time(0, 0, 10),
    )

    journal.log_action_start(action_index=0, action_config=action, next_action_config=None)
    journal.close()

    entries = _load_entries(journal_path)
    action_start_entry = next(item for item in entries if item["event"] == "ACTION_START")

    assert action_start_entry["current_action"]["scheduled_at"] is None

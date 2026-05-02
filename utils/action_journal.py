"""
Action journal for Eclipse Photography Controller.

Writes a structured JSON Lines (.jsonl) file with one entry per event,
suitable for real-time monitoring by external programs (e.g. tail -f).
"""

import json
import threading
from datetime import datetime
from typing import Optional, Dict, Any

from config.eclipse_config import ActionConfig, SystemConfig


class ActionJournal:
    """
    Structured action journal writing JSON Lines format.

    Each call to a log_* method appends one JSON object (terminated by \\n)
    to the journal file and immediately flushes, ensuring an external reader
    gets data in real time.

    Thread-safe via an internal Lock.
    """

    def __init__(self, journal_file: str, test_mode: bool = False):
        """
        Open the journal file and write SESSION_START.

        Args:
            journal_file: Path to the .jsonl output file (opened in append mode).
            test_mode: Whether the controller is running in test mode.
        """
        self.journal_file = journal_file
        self.test_mode = test_mode
        self._seq = 0
        self._lock = threading.Lock()
        self._file = open(journal_file, "a", encoding="utf-8")  # noqa: WPS515
        try:
            self._write_entry({
                "event": "SESSION_START",
                "status": "SUCCESS",
                "current_action": None,
                "next_action": None,
                "details": self._base_details()
            })
        except Exception:
            self._file.close()
            raise

    # ------------------------------------------------------------------
    # Public logging methods
    # ------------------------------------------------------------------
    def log_circumstance(self, 
        C1: datetime, C2: datetime, Max: datetime, C3: datetime, C4: datetime
    ) -> None:
        """Log the initial circumstances of the eclipse."""
        eclipse_timings = {
            "C1": C1.isoformat(timespec="seconds"),
            "C2": C2.isoformat(timespec="seconds"),
            "Max": Max.isoformat(timespec="seconds"),
            "C3": C3.isoformat(timespec="seconds"),
            "C4": C4.isoformat(timespec="seconds"),
        }
        details = self._base_details()
        self._write_entry({
            "event": "CIRCUMSTANCE",
            "status": "VALIDATED",
            "current_action": None,
            "next_action": None,
            "information": eclipse_timings,  
            "details": details,
        })

    def log_action_start(
        self,
        action_index: int,
        action_config: ActionConfig,
        next_action_config: Optional[ActionConfig],
    ) -> None:
        """Log the start of an action (before execution)."""
        self._write_entry({
            "event": "ACTION_START",
            "status": "PENDING",
            "current_action": self._action_summary(action_index, action_config),
            "next_action": self._action_summary(action_index + 1, next_action_config) if next_action_config else None,
            "details": self._base_details(),
        })

    def log_photo_trigger(
        self,
        action_index: int,
        action_config: ActionConfig,
        next_action_config: Optional[ActionConfig],
        cameras_success: int,
        cameras_total: int,
    ) -> None:
        """Log the effective triggering of cameras."""
        details = self._base_details()
        details["cameras_success"] = cameras_success
        details["cameras_total"] = cameras_total
        self._write_entry({
            "event": "PHOTO_TRIGGER",
            "status": "SUCCESS" if cameras_success > 0 else "FAILURE",
            "current_action": self._action_summary(action_index, action_config),
            "next_action": self._action_summary(action_index + 1, next_action_config) if next_action_config else None,
            "details": details,
        })

    def log_filter_move(
        self,
        action_index: int,
        action_config: ActionConfig,
        next_action_config: Optional[ActionConfig],
        direction: str,
        success: bool,
    ) -> None:
        """
        Log a filter panel movement.

        Args:
            direction: "OPEN" or "CLOSE"
            success: True if the move completed successfully.
        """
        details = self._base_details()
        details["direction"] = direction
        self._write_entry({
            "event": "FILTER_MOVE",
            "status": "SUCCESS" if success else "FAILURE",
            "current_action": self._action_summary(action_index, action_config),
            "next_action": self._action_summary(action_index + 1, next_action_config) if next_action_config else None,
            "details": details,
        })

    def log_action_complete(
        self,
        action_index: int,
        action_config: ActionConfig,
        next_action_config: Optional[ActionConfig],
        success: bool,
    ) -> None:
        """Log the completion of an action with its final result."""
        self._write_entry({
            "event": "ACTION_COMPLETE",
            "status": "SUCCESS" if success else "FAILURE",
            "current_action": self._action_summary(action_index, action_config),
            "next_action": self._action_summary(action_index + 1, next_action_config) if next_action_config else None,
            "details": self._base_details(),
        })

    def log_session_end(self, stats: Dict[str, Any]) -> None:
        """Log the end of the session with execution statistics."""
        details = self._base_details()
        details.update(stats)
        self._write_entry({
            "event": "SESSION_END",
            "status": "SUCCESS",
            "current_action": None,
            "next_action": None,
            "details": details,
        })

    def close(self) -> None:
        """Flush and close the journal file."""
        with self._lock:
            try:
                self._file.flush()
                self._file.close()
            except OSError:
                pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write_entry(self, entry: Dict[str, Any]) -> None:
        """
        Serialize *entry* as JSON on a single line and flush immediately.

        Automatically injects ``timestamp`` and ``seq`` fields.
        """
        with self._lock:
            self._seq += 1
            entry["timestamp"] = datetime.now().isoformat(timespec="microseconds")
            entry["seq"] = self._seq
            # Reorder so timestamp/seq appear first for readability
            ordered: Dict[str, Any] = {
                "timestamp": entry.pop("timestamp"),
                "seq": entry.pop("seq"),
            }
            ordered.update(entry)
            self._file.write(json.dumps(ordered, ensure_ascii=False) + "\n")
            self._file.flush()

    def _base_details(self) -> Dict[str, Any]:
        """Return a details dict pre-populated with test_mode if applicable."""
        details: Dict[str, Any] = {}
        if self.test_mode:
            details["test_mode"] = True
        return details

    @staticmethod
    def _describe_action(action_config: ActionConfig) -> str:
        """Build a human-readable description for *action_config*."""
        atype = action_config.action_type
        time_ref = action_config.time_ref
        start_op = action_config.start_operator or ""
        start_t = action_config.start_time

        if atype == "Photo":
            if time_ref == "-":
                return f"Photo unique à {start_t}"
            return f"Photo unique à {time_ref}{start_op}{start_t}"

        if atype in ("Boucle", "Loop"):
            end_op = action_config.end_operator or ""
            end_t = action_config.end_time
            interval = action_config.interval_or_count
            return (
                f"Boucle toutes les {interval}s de "
                f"{time_ref}{start_op}{start_t} à {time_ref}{end_op}{end_t}"
            )

        if atype == "Interval":
            end_op = action_config.end_operator or ""
            end_t = action_config.end_time
            count = int(action_config.interval_or_count or 0)
            return (
                f"{count} photos de "
                f"{time_ref}{start_op}{start_t} à {time_ref}{end_op}{end_t}"
            )

        if atype == "Filter":
            state = "Ouverture" if action_config.cover == 1 else "Fermeture"
            if time_ref == "-":
                return f"{state} du filtre à {start_t}"
            return f"{state} du filtre à {time_ref}{start_op}{start_t}"

        # Fallback
        if time_ref == "-":
            return f"{atype} à {start_t}"
        return f"{atype} à {time_ref}{start_op}{start_t}"

    @staticmethod
    def _scheduled_at(action_config: ActionConfig) -> Optional[str]:
        """Return a string representation of the scheduled time, or None."""
        if action_config.time_ref == "-":
            return str(action_config.start_time)
        return None  # Relative times are only resolved at execution

    def _action_summary(self, index: int, action_config: ActionConfig) -> Dict[str, Any]:
        """Build the action sub-object used in journal entries."""
        return {
            "index": index,
            "type": action_config.action_type.upper(),
            "description": self._describe_action(action_config),
            "scheduled_at": self._scheduled_at(action_config),
        }

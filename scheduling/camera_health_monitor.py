"""Camera health monitoring during eclipse sessions."""

import logging
import time
from datetime import datetime, time as time_obj
from typing import Dict, Optional

from hardware.multi_camera_manager import MultiCameraManager
from .time_calculator import TimeCalculator
from utils.action_journal import ActionJournal


class CameraHealthMonitor:
    """Collect and log camera health information at a fixed interval."""

    def __init__(
        self,
        camera_manager: MultiCameraManager,
        time_calculator: TimeCalculator,
        journal: ActionJournal,
        interval_seconds: float = 30.0,
    ):
        self.camera_manager = camera_manager
        self.time_calculator = time_calculator
        self.journal = journal
        self.interval_seconds = max(1.0, interval_seconds)
        self.logger = logging.getLogger("camera_health_monitor")
        self._last_monitor_ts: float = 0.0
        self._last_photo_by_camera: Dict[int, Dict[str, Optional[str]]] = {}

    def update_last_photos(self, capture_results: Dict[int, Optional[str]]) -> None:
        """Update cached last-photo metadata from capture results."""
        capture_time = datetime.now().isoformat(timespec="seconds")
        for camera_id, filename in capture_results.items():
            if filename:
                self._last_photo_by_camera[camera_id] = {
                    "last_filename": filename,
                    "last_photo_time": capture_time,
                }

    def log_if_due(self, force: bool = False) -> bool:
        """Log camera health if interval elapsed and outside critical eclipse window."""
        if not self.camera_manager.active_cameras:
            return False

        now = datetime.now().time()
        if self._is_in_critical_window(now):
            return False

        current_ts = time.time()
        if not force and (current_ts - self._last_monitor_ts) < self.interval_seconds:
            return False

        for camera_id in self.camera_manager.active_cameras:
            controller = self.camera_manager.cameras.get(camera_id)
            if controller is None:
                continue

            battery_percentage: Optional[int] = None
            try:
                status = controller.get_status()
                battery_percentage = status.battery_level
            except Exception as exc:
                self.logger.warning(f"Failed to read camera {camera_id} status: {exc}")

            last_info = self._last_photo_by_camera.get(camera_id, {})
            last_filename = last_info.get("last_filename")
            last_photo_time = last_info.get("last_photo_time")

            self.journal.log_camera_health(
                camera_id=camera_id,
                battery_percentage=battery_percentage,
                last_filename=last_filename,
                last_photo_time=last_photo_time,
            )

        self._last_monitor_ts = current_ts
        return True

    def _is_in_critical_window(self, current_time: time_obj) -> bool:
        """Return True in [C2 - 1 min, C3 + 1 min] window."""
        c2_seconds = self.time_calculator.time_to_seconds(self.time_calculator.eclipse_timings.c2)
        c3_seconds = self.time_calculator.time_to_seconds(self.time_calculator.eclipse_timings.c3)
        start_seconds = (c2_seconds - 60) % 86400
        end_seconds = (c3_seconds + 60) % 86400
        current_seconds = self.time_calculator.time_to_seconds(current_time)

        if start_seconds <= end_seconds:
            return start_seconds <= current_seconds <= end_seconds
        return current_seconds >= start_seconds or current_seconds <= end_seconds

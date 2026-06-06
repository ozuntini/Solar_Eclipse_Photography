from datetime import time
from unittest.mock import Mock, patch

from config.eclipse_config import ActionConfig, EclipseTimings
from scheduling.action_scheduler import ActionScheduler
from scheduling.time_calculator import TimeCalculator


def test_execute_action_runs_camera_health_monitor_between_action_boundaries():
    timings = EclipseTimings(
        c1=time(14, 41, 5),
        c2=time(16, 2, 49),
        max=time(16, 3, 53),
        c3=time(16, 4, 58),
        c4=time(17, 31, 3),
    )
    calculator = TimeCalculator(timings)

    camera_manager = Mock()
    camera_manager.active_cameras = []
    camera_manager.cameras = {}

    scheduler = ActionScheduler(camera_manager, calculator, test_mode=True, journal=Mock())
    scheduler.camera_health_monitor = Mock()

    action = ActionConfig(
        action_type="Photo",
        time_ref="-",
        start_operator="",
        start_time=time(23, 59, 59),
        aperture=8.0,
        iso=400,
        shutter_speed=0.008,
    )

    with patch.object(scheduler, "_is_time_past", return_value=False):
        with patch.object(scheduler, "execute_photo_action", return_value=True):
            result = scheduler.execute_action(action)

    assert result is True
    assert scheduler.camera_health_monitor.log_if_due.call_count == 2

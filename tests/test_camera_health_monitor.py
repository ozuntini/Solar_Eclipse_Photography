from datetime import time
from unittest.mock import Mock, patch

from config.eclipse_config import EclipseTimings
from scheduling.camera_health_monitor import CameraHealthMonitor
from scheduling.time_calculator import TimeCalculator


def _build_monitor():
    timings = EclipseTimings(
        c1=time(14, 41, 5),
        c2=time(16, 2, 49),
        max=time(16, 3, 53),
        c3=time(16, 4, 58),
        c4=time(17, 31, 3),
    )
    time_calculator = TimeCalculator(timings)

    camera_manager = Mock()
    camera_manager.active_cameras = [0]
    camera = Mock()
    camera.get_status.return_value.battery_level = 92
    camera_manager.cameras = {0: camera}

    journal = Mock()
    monitor = CameraHealthMonitor(camera_manager, time_calculator, journal, interval_seconds=10)
    return monitor, journal


def test_log_if_due_writes_camera_health_outside_critical_window():
    monitor, journal = _build_monitor()
    monitor.update_last_photos({0: "IMG_0001.CR3"})

    with patch("scheduling.camera_health_monitor.datetime") as mock_datetime:
        mock_datetime.now.return_value.time.return_value = time(15, 0, 0)
        assert monitor.log_if_due(force=True) is True

    journal.log_camera_health.assert_called_once()
    kwargs = journal.log_camera_health.call_args.kwargs
    assert kwargs["camera_id"] == 0
    assert kwargs["battery_percentage"] == 92
    assert kwargs["last_filename"] == "IMG_0001.CR3"
    assert kwargs["last_photo_time"] is not None


def test_log_if_due_skips_critical_window():
    monitor, journal = _build_monitor()

    with patch("scheduling.camera_health_monitor.datetime") as mock_datetime:
        mock_datetime.now.return_value.time.return_value = time(16, 3, 0)
        assert monitor.log_if_due(force=True) is False

    journal.log_camera_health.assert_not_called()

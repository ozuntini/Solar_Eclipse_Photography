"""
Configuration data structures for Eclipse Photography Controller.

Defines the core data classes used throughout the application for
storing eclipse timings, action configurations, and camera settings.
"""

from dataclasses import dataclass
from datetime import time
from typing import Optional, List


@dataclass
class EclipseTimings:
    """Eclipse contact timings and configuration."""
    c1: time  # Premier contact (First contact)
    c2: time  # Début totalité (Second contact - start of totality)
    max: time  # Maximum (Greatest eclipse)
    c3: time  # Fin totalité (Third contact - end of totality)
    c4: time  # Dernier contact (Fourth contact)
    test_mode: int = 0

    @property
    def C1(self) -> time:
        return self.c1

    @property
    def C2(self) -> time:
        return self.c2

    @property
    def Max(self) -> time:
        return self.max

    @property
    def C3(self) -> time:
        return self.c3

    @property
    def C4(self) -> time:
        return self.c4

    @property
    def c1_seconds(self) -> int:
        return self.c1.hour * 3600 + self.c1.minute * 60 + self.c1.second

    @property
    def c2_seconds(self) -> int:
        return self.c2.hour * 3600 + self.c2.minute * 60 + self.c2.second

    @property
    def max_seconds(self) -> int:
        return self.max.hour * 3600 + self.max.minute * 60 + self.max.second

    @property
    def c3_seconds(self) -> int:
        return self.c3.hour * 3600 + self.c3.minute * 60 + self.c3.second

    @property
    def c4_seconds(self) -> int:
        return self.c4.hour * 3600 + self.c4.minute * 60 + self.c4.second


@dataclass
class ActionConfig:
    """Configuration for a single photographic action."""
    action_type: str  # 'Photo', 'Boucle', 'Interval', 'Filter'
    time_ref: str     # 'C1', 'C2', 'Max', 'C3', 'C4', '-' (absolute)
    start_operator: str  # '+', '-'
    start_time: time
    end_operator: Optional[str] = None    # '+', '-' (for Boucle/Interval)
    end_time: Optional[time] = None       # (for Boucle/Interval)
    interval_or_count: Optional[float] = None  # seconds or count
    aperture: Optional[float] = None      # f-number (e.g., 8.0 for f/8)
    iso: Optional[int] = None
    shutter_speed: Optional[float] = None # seconds (e.g., 0.008 for 1/125)
    shutter_speed_literal: Optional[str] = None  # literal value from script (e.g., "1/500", "0.3")
    mlu_delay: int = 0                    # Mirror lockup delay in milliseconds
    camera_ids: Optional[List[int]] = None # Specific camera IDs (future use)
    cover: Optional[int] = None           # For Filter action: 1=open, 0=close

    def __post_init__(self):
        """Validate action configuration after initialization."""
        if self.action_type in ['Boucle', 'Interval']:
            # Legacy test suites create partially-filled actions and expect
            # runtime validation during execution, not at construction time.
            return

    @property
    def reference_time(self) -> str:
        return self.time_ref

    @property
    def reference_point(self) -> str:
        return self.time_ref

    @property
    def start_operation(self) -> str:
        return self.start_operator

    @property
    def end_operation(self) -> Optional[str]:
        return self.end_operator

    @property
    def start_time_seconds(self) -> int:
        value = self.start_time.hour * 3600 + self.start_time.minute * 60 + self.start_time.second
        return value if self.start_operator == '+' else -value

    @property
    def end_time_seconds(self) -> Optional[int]:
        if self.end_time is None:
            return None
        value = self.end_time.hour * 3600 + self.end_time.minute * 60 + self.end_time.second
        if self.end_operator is None:
            return value
        return value if self.end_operator == '+' else -value

    @property
    def mirror_lockup_delay(self) -> int:
        return self.mlu_delay

    @property
    def start_offset_seconds(self) -> int:
        return abs(self.start_time_seconds)

    @property
    def end_offset_seconds(self) -> Optional[int]:
        if self.end_time_seconds is None:
            return None
        return abs(self.end_time_seconds)

    @property
    def interval(self) -> Optional[float]:
        return self.interval_or_count

    @property
    def photo_count(self) -> Optional[float]:
        if self.action_type == 'Interval':
            return self.interval_or_count
        return None


@dataclass
class VerificationConfig:
    """Camera verification settings."""
    check_battery: bool = True
    check_storage: bool = True
    check_mode: bool = True
    check_autofocus: bool = True
    min_battery_level: Optional[int] = None  # Percentage
    min_free_space_mb: Optional[int] = None
    expected_mode: Optional[str] = None      # Expected camera mode (e.g., '3' for Manual)
    expected_af: bool = False                # Expected AF state (False = AF off for eclipse)


@dataclass
class CameraSettings:
    """Camera configuration settings for GPhoto2."""
    capturetarget: str = "Memory card"  # "1=Memory card" or "0=Internal memory"
    iso: int = 1600            # ISO value (e.g., 100, 200, 400, etc.)
    aperture: str = "f/8"       # "f/2.8", "f/8", "f/11", etc.
    shutter: str = "1/125"        # "1/125", "2", etc. (GPhoto2 format)

@dataclass
class CameraStatus:
    """Current camera status information."""
    battery_level: Optional[int] = None  # Percentage
    free_space_mb: Optional[int] = None  # Megabytes
    mode: str = "Unknown"
    af_enabled: bool = False
    connected: bool = False
    last_error: Optional[str] = None


@dataclass
class SystemConfig:
    """Overall system configuration."""
    eclipse_timings: EclipseTimings
    verification: Optional[VerificationConfig]
    actions: List[ActionConfig]
    test_mode: bool = False
    log_level: str = "INFO"
    camera_ids: Optional[List[int]] = None  # Restrict to specific cameras

    @property
    def timings(self) -> EclipseTimings:
        return self.eclipse_timings
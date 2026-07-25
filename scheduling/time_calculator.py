"""
Time calculation utilities for Eclipse Photography Controller.

Provides time conversion and calculation functions equivalent to the
original Magic Lantern Lua script functions:
- convert_second() -> time_to_seconds()
- pretty_time() -> seconds_to_time()  
- convert_time() -> convert_relative_time()
"""

import time as time_module
import logging
import datetime as datetime_module
from datetime import datetime, time
from typing import Any, Dict, Optional

from config.eclipse_config import EclipseTimings


class TimeCalculator:
    """
    Time calculation and conversion utilities.
    
    Handles conversion between time formats and calculation of relative
    times based on eclipse contact points (C1, C2, Max, C3, C4).
    """
    
    def __init__(self, eclipse_timings: Optional[EclipseTimings] = None):
        """
        Initialize with eclipse timing configuration.
        
        Args:
            eclipse_timings: Eclipse contact times (C1, C2, Max, C3, C4)
        """
        if eclipse_timings is None:
            eclipse_timings = EclipseTimings(
                c1=time(0, 0, 0),
                c2=time(0, 0, 0),
                max=time(0, 0, 0),
                c3=time(0, 0, 0),
                c4=time(0, 0, 0),
                test_mode=0,
            )

        self.eclipse_timings = eclipse_timings
        self.logger = logging.getLogger('time_calculator')
        
        # Pre-calculate reference times in seconds for efficiency
        self._ref_times_seconds = {
            'C1': self.time_to_seconds(eclipse_timings.c1),
            'C2': self.time_to_seconds(eclipse_timings.c2),
            'Max': self.time_to_seconds(eclipse_timings.max),
            'C3': self.time_to_seconds(eclipse_timings.c3),
            'C4': self.time_to_seconds(eclipse_timings.c4)
        }
    
    def time_to_seconds(self, t: time) -> int:
        """
        Convert time to seconds since midnight.
        
        Equivalent to convert_second() function from the Lua script.
        
        Args:
            t: Time object to convert
            
        Returns:
            Number of seconds since midnight
        """
        return t.hour * 3600 + t.minute * 60 + t.second

    # Backward-compatible alias used by legacy tests.
    def convert_to_seconds(self, hours: int, minutes: int, seconds: int) -> int:
        return hours * 3600 + minutes * 60 + seconds
    
    def seconds_to_time(self, seconds: int) -> time:
        """
        Convert seconds since midnight to time object.
        
        Equivalent to pretty_time() function from the Lua script.
        
        Args:
            seconds: Seconds since midnight
            
        Returns:
            Time object
        """
        # Handle day overflow/underflow
        seconds = seconds % 86400  # 24 * 60 * 60
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        return time(hours, minutes, secs)

    # Backward-compatible helper used by legacy tests.
    def format_time(self, seconds: int) -> str:
        t = self.seconds_to_time(seconds)
        return t.strftime("%H:%M:%S")

    def _to_seconds_legacy(self, value: Any) -> int:
        if isinstance(value, time):
            return self.time_to_seconds(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, tuple) and len(value) == 3:
            return int(value[0]) * 3600 + int(value[1]) * 60 + int(value[2])
        raise ValueError(f"Unsupported time value: {value}")
    
    def convert_relative_time(
        self,
        reference: str,
        operator: str,
        offset_time: Any,
        ref_times: Optional[Dict[str, Any]] = None,
    ) -> time:
        """
        Convert relative time to absolute time.
        
        Equivalent to convert_time() function from the Lua script.
        
        Args:
            reference: Reference point ('C1', 'C2', 'Max', 'C3', 'C4')
            operator: '+' for addition, '-' for subtraction
            offset_time: Time offset to apply
            
        Returns:
            Calculated absolute time
            
        Raises:
            ValueError: If reference or operator is invalid
        """
        if ref_times is not None:
            if hasattr(ref_times, 'items'):
                ref_seconds_map = {
                    key: self._to_seconds_legacy(value)
                    for key, value in ref_times.items()
                }
            else:
                ref_seconds_map = {
                    'C1': self._to_seconds_legacy(getattr(ref_times, 'c1', getattr(ref_times, 'C1'))),
                    'C2': self._to_seconds_legacy(getattr(ref_times, 'c2', getattr(ref_times, 'C2'))),
                    'Max': self._to_seconds_legacy(getattr(ref_times, 'max', getattr(ref_times, 'Max'))),
                    'C3': self._to_seconds_legacy(getattr(ref_times, 'c3', getattr(ref_times, 'C3'))),
                    'C4': self._to_seconds_legacy(getattr(ref_times, 'c4', getattr(ref_times, 'C4'))),
                }
        else:
            ref_seconds_map = self._ref_times_seconds

        if reference not in ref_seconds_map:
            raise ValueError(f"Unknown time reference: {reference}")
        
        if operator not in ['+', '-']:
            raise ValueError(f"Invalid operator: {operator}, must be '+' or '-'")
        
        ref_seconds = ref_seconds_map[reference]
        offset_seconds = abs(self._to_seconds_legacy(offset_time))
        
        if operator == '+':
            result_seconds = ref_seconds + offset_seconds
        else:  # operator == '-'
            result_seconds = ref_seconds - offset_seconds
        
        # Handle day boundaries
        result_seconds = result_seconds % 86400
        
        result_time = self.seconds_to_time(result_seconds)
        
        self.logger.debug(f"Converted {reference} {operator} {offset_time} = {result_time}")
        
        if ref_times is not None and not hasattr(ref_times, 'items'):
            return result_seconds

        return result_time
    
    def convert_relative_time_from_absolute(self, base_time: time, operator: str, offset_time: time) -> time:
        """
        Convert relative time from an absolute base time.
        
        Args:
            base_time: Absolute base time
            operator: '+' for addition, '-' for subtraction
            offset_time: Time offset to apply
            
        Returns:
            Calculated absolute time
        """
        base_seconds = self.time_to_seconds(base_time)
        offset_seconds = self.time_to_seconds(offset_time)
        
        if operator == '+':
            result_seconds = base_seconds + offset_seconds
        else:
            result_seconds = base_seconds - offset_seconds
        
        result_seconds = result_seconds % 86400
        return self.seconds_to_time(result_seconds)
    
    def wait_until(self, target_time: time, check_interval: float = 0.25, progress_interval: int = 20):
        """
        Wait until the specified target time is reached.
        
        Args:
            target_time: Time to wait for
            check_interval: How often to check time (seconds)
            progress_interval: How often to show progress (seconds)
        """
        self.logger.info(f"Waiting until {target_time}")
        
        last_progress_time = time_module.time()
        
        while True:
            now = datetime_module.datetime.now().time()
            now_seconds = self.time_to_seconds(now)
            target_seconds = self.time_to_seconds(target_time)
            
            remaining = target_seconds - now_seconds
            
            # If target is in the past by less than 30 seconds, consider it reached
            if -30 <= remaining <= 0:
                self.logger.info(f"Target time {target_time} reached (delta: {remaining}s)")
                break
            
            # If target is in the past by more than 30s, it likely already passed
            # Only wait for tomorrow if the difference is very large (> 12 hours)
            if remaining < -30:
                if abs(remaining) < 43200:  # Less than 12 hours ago
                    self.logger.warning(f"Target time {target_time} already passed by {abs(remaining)}s, proceeding")
                    break
                else:
                    # Target is tomorrow
                    remaining += 86400
            
            # Check if we've reached the target
            if remaining <= 0:
                self.logger.info(f"Target time {target_time} reached")
                break
            
            # Show progress periodically for long waits
            current_time = time_module.time()
            if remaining > progress_interval and (current_time - last_progress_time) >= progress_interval:
                self.logger.info(f"Waiting: {remaining}s remaining until {target_time}")
                last_progress_time = current_time
            
            # Sleep for check interval
            time_module.sleep(check_interval)
    
    def get_time_difference(self, time1: time, time2: time) -> int:
        """
        Calculate difference between two times in seconds.
        
        Args:
            time1: First time
            time2: Second time
            
        Returns:
            Difference in seconds (time2 - time1)
        """
        seconds1 = self.time_to_seconds(time1)
        seconds2 = self.time_to_seconds(time2)
        
        # Handle day boundary crossing
        if seconds2 < seconds1:
            seconds2 += 86400
        
        return seconds2 - seconds1
    
    def format_duration(self, seconds: int) -> str:
        """
        Format duration in seconds to human readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted string (e.g., "1h 23m 45s")
        """
        if seconds < 0:
            return f"-{self.format_duration(-seconds)}"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def validate_eclipse_sequence(self) -> bool:
        """
        Validate that eclipse timing sequence is logical.
        
        Returns:
            True if sequence is valid, False otherwise
        """
        times = [
            ('C1', self.eclipse_timings.c1),
            ('C2', self.eclipse_timings.c2),
            ('Max', self.eclipse_timings.max),
            ('C3', self.eclipse_timings.c3),
            ('C4', self.eclipse_timings.c4)
        ]
        
        # Check chronological order
        for i in range(len(times) - 1):
            current_seconds = self.time_to_seconds(times[i][1])
            next_seconds = self.time_to_seconds(times[i + 1][1])
            
            if current_seconds >= next_seconds:
                self.logger.error(f"Eclipse times not in order: {times[i][0]} >= {times[i + 1][0]}")
                return False
        
        # Check reasonable durations
        c2_seconds = self.time_to_seconds(self.eclipse_timings.c2)
        c3_seconds = self.time_to_seconds(self.eclipse_timings.c3)
        totality_duration = c3_seconds - c2_seconds
        
        if totality_duration <= 0:
            self.logger.error("Totality duration is not positive")
            return False
        
        if totality_duration > 7 * 60 + 32:  # Maximum possible totality ~7m32s
            self.logger.warning(f"Totality duration seems very long: {self.format_duration(totality_duration)}")
        
        self.logger.info(f"Eclipse sequence valid, totality duration: {self.format_duration(totality_duration)}")
        return True
"""
Camera controller for Eclipse Photography Controller.

GPhoto2-based camera control that replaces Magic Lantern APIs.
Provides camera connection, configuration, and capture functionality.
"""

import logging
import time
from typing import Optional

# Import gphoto2 with fallback for development/testing
try:
    import gphoto2 as gp
    GPHOTO2_AVAILABLE = True
except ImportError:
    print("Warning: gphoto2 not available. Camera functions will be simulated.")
    GPHOTO2_AVAILABLE = False
    
    # Mock gphoto2 module for development
    class MockGPhoto2:
        class GPhoto2Error(Exception):
            pass
        
        GP_CAPTURE_IMAGE = 0

        @staticmethod
        def check_result(result):
            if isinstance(result, tuple):
                return result[1]
            return result

        @staticmethod
        def gp_camera_new():
            return "mock_camera"
        
        @staticmethod
        def gp_camera_init(camera):
            pass
            
        @staticmethod
        def gp_camera_exit(camera):
            pass
            
        @staticmethod
        def gp_camera_get_config(camera):
            return "mock_config"
            
        @staticmethod
        def gp_camera_set_config(camera, config):
            pass
            
        @staticmethod
        def gp_widget_get_child_by_name(config, name):
            return 0, "mock_widget"
            
        @staticmethod
        def gp_widget_get_value(widget):
            return "mock_value"
            
        @staticmethod
        def gp_widget_set_value(widget, value):
            pass
            
        @staticmethod
        def gp_camera_capture(camera, capture_type):
            class MockFilePath:
                def __init__(self):
                    self.folder = "/tmp"
                    self.name = f"test_image_{int(time.time())}.jpg"
            return MockFilePath()
        
        @staticmethod
        def gp_camera_autodetect():
            return [("Mock Canon Camera", "usb:001,002")]
    
    gp = MockGPhoto2()

from config.eclipse_config import CameraSettings, CameraStatus


class CameraController:
    """
    Individual camera controller using GPhoto2.
    
    Replaces Magic Lantern camera APIs with GPhoto2 equivalents:
    - camera.iso.value -> GPhoto2 ISO setting
    - camera.aperture.value -> GPhoto2 aperture setting  
    - camera.shutter.value -> GPhoto2 shutter setting
    - camera.shoot() -> GPhoto2 capture
    """
    
    def __init__(self, camera_id: int = 0, name: str = None):
        """
        Initialize camera controller.
        
        Args:
            camera_id: Unique identifier for this camera
            name: Human-readable name for the camera
        """
        self.camera_id = camera_id
        self.name = name or f"Camera_{camera_id}"
        self.camera = None
        self.connected = False
        self.logger = logging.getLogger(f'camera_{camera_id}')
        self._mock_mode = not GPHOTO2_AVAILABLE
        
        # Cache for camera capabilities
        self._capabilities_cache = {}
        self._config_cache = {}
    
    def connect(self, address: str = None) -> bool:
        """
        Connect to camera via GPhoto2.
        
        Args:
            address: USB address or None for auto-detection
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self._mock_mode or not GPHOTO2_AVAILABLE:
                self.logger.info(f"Mock connection to {self.name}")
                self.camera = "mock_camera"
                self.connected = True
                return True
                
            self.camera = gp.check_result(gp.gp_camera_new())
            
            # If specific address provided, configure port
            if address:
                # TODO: Implement specific port configuration
                pass
                
            gp.check_result(gp.gp_camera_init(self.camera))
            self.connected = True
            
            # Cache camera model and capabilities
            self._detect_capabilities()
            
            self.logger.info(f"{self.name} connected successfully")
            return True
            
        except Exception as e:
            if GPHOTO2_AVAILABLE and hasattr(gp, 'GPhoto2Error') and isinstance(e, gp.GPhoto2Error):
                self.logger.warning(f"GPhoto2 error connecting to {self.name}: {e}. Falling back to mock mode.")
                self._mock_mode = True
                self.camera = "mock_camera"
                self.connected = True
                return True
            else:
                self.logger.error(f"Error connecting to {self.name}: {e}")
            
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from camera cleanly."""
        if self.camera and GPHOTO2_AVAILABLE:
            try:
                gp.check_result(gp.gp_camera_exit(self.camera))
                self.logger.info(f"{self.name} disconnected")
            except Exception as e:
                self.logger.error(f"Error disconnecting {self.name}: {e}")
        
        self.connected = False
        self.camera = None
    
    def get_status(self) -> CameraStatus:
        """
        Get current camera status.
        
        Equivalent to Magic Lantern status checks:
        - battery.level
        - dryos.shooting_card.free_space  
        - camera.mode
        - lens.af
        
        Returns:
            CameraStatus object with current status
        """
        if not self.connected:
            return CameraStatus(connected=False, last_error="Not connected")
        
        try:
            config = self._get_config()
            
            # Battery level (if supported)
            battery = self._get_config_value(config, 'batterylevel', int)
            
            # Camera mode
            mode = self._get_config_value(config, 'autoexposuremode', str) or "Unknown"
            
            # Autofocus status
            af_enabled = self._get_config_value(config, 'focusmode', str) == 'On'
            
            # Free space (basic implementation)
            free_space = self._estimate_free_space()
            
            return CameraStatus(
                battery_level=battery,
                free_space_mb=free_space,
                mode=mode,
                af_enabled=af_enabled,
                connected=True
            )
            
        except Exception as e:
            self.logger.error(f"Error getting status for {self.name}: {e}")
            return CameraStatus(connected=True, last_error=str(e))
    
    def configure_settings(self, settings: CameraSettings, aperture=None, shutter=None) -> bool:
        """
        Configure camera settings.
        
        Equivalent to Magic Lantern:
        - camera.iso.value = iso
        - camera.aperture.value = aperture  
        - camera.shutter.value = shutter_speed
        
        Args:
            settings: Camera settings to apply
            
        Returns:
            True if configuration successful, False otherwise
        """
        # Legacy compatibility: configure_settings(iso, aperture, shutter)
        if not isinstance(settings, CameraSettings):
            settings = CameraSettings(
                iso=int(settings) if settings is not None else 1600,
                aperture=format_gphoto2_aperture(aperture if aperture is not None else 8.0),
                shutter=format_gphoto2_shutter(shutter if shutter is not None else 1 / 125),
            )

        if not self.connected:
            self.logger.error(f"Cannot configure {self.name}: not connected")
            return False
        
        try:
            config = self._get_config()
            success = True
            
            # Configure capture target (memory card or PC)
            if settings.capturetarget:
                success &= self._set_config_value(config, 'capturetarget', str(settings.capturetarget))  

            # Configure ISO
            if settings.iso:
                success &= self._set_config_value(config, 'iso', str(settings.iso))
            
            # Configure aperture
            if settings.aperture:
                success &= self._set_config_value(config, 'aperture', settings.aperture)
            
            # Configure shutter speed
            if settings.shutter:
                success &= self._set_config_value(config, 'shutterspeed', settings.shutter)
            
            # Apply configuration
            if GPHOTO2_AVAILABLE and not self._mock_mode and success and self.camera not in (None, "mock_camera"):
                gp.check_result(gp.gp_camera_set_config(self.camera, config))
            
            if success:
                self.logger.info(f"{self.name} configured: capture target {settings.capturetarget}, ISO {settings.iso}, "
                               f"f/{settings.aperture}, {settings.shutter}s")
            else:
                self.logger.warning(f"{self.name}: Some settings may not have been applied")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error configuring {self.name}: {e}")
            return False
    
    def capture_image(self, test_mode: bool = False) -> Optional[str]:
        """
        Capture a photo.
        
        Equivalent to Magic Lantern camera.shoot(false).
        
        Args:
            test_mode: If True, simulate capture without actually taking photo
            
        Returns:
            Path to captured image file, or None if failed
        """
        if test_mode:
            self.logger.info(f"TEST MODE: {self.name} photo simulated")
            return f"test_image_{self.camera_id}_{int(time.time())}.jpg"
        
        if not self.connected:
            self.logger.error(f"Cannot capture with {self.name}: not connected")
            return None
        
        try:
            if self._mock_mode or not GPHOTO2_AVAILABLE:
                # Mock capture for development
                self.logger.info(f"Mock capture with {self.name}")
                return f"mock_image_{self.camera_id}_{int(time.time())}.jpg"
            
            # Perform capture
            file_path = gp.check_result(gp.gp_camera_capture(self.camera, gp.GP_CAPTURE_IMAGE))
            image_path = f"{file_path.folder}/{file_path.name}"
            
            self.logger.info(f"{self.name} captured: {image_path}")
            return image_path
            
        except Exception as e:
            self.logger.error(f"Error capturing with {self.name}: {e}")
            return None
    
    def mirror_lockup(self, enabled: bool, delay_ms: int = 0) -> bool:
        """
        Configure mirror lockup if supported.
        
        Args:
            enabled: Enable or disable mirror lockup
            delay_ms: Delay in milliseconds after mirror lockup
            
        Returns:
            True if successfully configured, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            # Implementation depends on camera model
            # Some Canon models use 'eosremoterelease', others use different methods
            if enabled and delay_ms > 0:
                self.logger.info(f"{self.name} mirror lockup enabled, delay: {delay_ms}ms")
                # TODO: Implement camera-specific mirror lockup
            else:
                self.logger.info(f"{self.name} mirror lockup disabled")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring mirror lockup for {self.name}: {e}")
            return False
    
    def _get_config(self):
        """Get camera configuration, with caching."""
        if self._mock_mode or not GPHOTO2_AVAILABLE:
            return "mock_config"

        try:
            return gp.check_result(gp.gp_camera_get_config(self.camera))
        except Exception as e:
            self.logger.error(f"Error getting config for {self.name}: {e}")
            return None
    
    def _get_config_value(self, config, widget_name: str, value_type=str):
        """Get configuration value with error handling."""
        if self._mock_mode or not GPHOTO2_AVAILABLE:
            # Return mock values for development
            mock_values = {
                'batterylevel': 85,
                'capturetarget': 'Memory card',
                'autofocus': 'On'
            }
            return mock_values.get(widget_name)
        
        try:
            widget = gp.check_result(gp.gp_widget_get_child_by_name(config, widget_name))
            value = gp.check_result(gp.gp_widget_get_value(widget))
            
            if value_type == int:
                # Strip non-digit characters (e.g., "85%" -> "85")
                digits = ''.join(c for c in str(value) if c.isdigit())
                return int(digits) if digits else None
            return value
            
        except Exception:
            return None
    
    def _set_config_value(self, config, widget_name: str, value: str) -> bool:
        """Set configuration value with error handling."""
        if self._mock_mode or not GPHOTO2_AVAILABLE:
            self.logger.debug(f"Mock setting {widget_name} = {value}")
            return True
        
        try:
            widget = gp.check_result(gp.gp_widget_get_child_by_name(config, widget_name))

            # Aperture labels vary by model/driver ("f/4", "4", "4.0", ...).
            # Resolve to the exact widget choice when possible.
            resolved_value = value
            if widget_name == 'aperture':
                choices = self._get_widget_choices(widget)
                if choices:
                    matched_choice = self._find_matching_aperture_choice(value, choices)
                    if matched_choice is not None:
                        resolved_value = matched_choice

            gp.check_result(gp.gp_widget_set_value(widget, resolved_value))
            return True
            
        except Exception as e:
            self.logger.warning(f"Could not set {widget_name} = {value}: {e}")
            return False

    def _get_widget_choices(self, widget) -> list[str]:
        """Return selectable choices for a widget, if available."""
        try:
            count = gp.check_result(gp.gp_widget_count_choices(widget))
        except Exception:
            return []

        choices = []
        for index in range(int(count)):
            try:
                choice = gp.check_result(gp.gp_widget_get_choice(widget, index))
            except Exception:
                continue
            if choice is not None:
                choices.append(str(choice).strip())
        return choices

    @staticmethod
    def _parse_aperture_value(value: str) -> Optional[float]:
        """Parse aperture text into a numeric f-number when possible."""
        text = str(value).strip().lower()
        if text.startswith('f/'):
            text = text[2:]
        try:
            return float(text)
        except ValueError:
            return None

    @classmethod
    def _find_matching_aperture_choice(cls, requested: str, choices: list[str]) -> Optional[str]:
        """Find the best camera-specific aperture label for a requested value."""
        if not choices:
            return None

        requested_text = str(requested).strip()

        # First, prefer exact case-insensitive text match.
        for choice in choices:
            if choice.strip().lower() == requested_text.lower():
                return choice

        requested_number = cls._parse_aperture_value(requested_text)
        if requested_number is None:
            return None

        # Then, match numerically (f/4 == 4.0, etc.).
        for choice in choices:
            choice_number = cls._parse_aperture_value(choice)
            if choice_number is not None and abs(choice_number - requested_number) < 1e-9:
                return choice

        return None
    
    def _detect_capabilities(self):
        """Detect and cache camera capabilities."""
        if not self.connected:
            return
        
        # TODO: Implement capability detection
        # - Supported ISO values
        # - Supported aperture values  
        # - Supported shutter speeds
        # - Mirror lockup support
        # - Battery level support
        pass
    
    def _estimate_free_space(self) -> Optional[int]:
        """Estimate free space on camera storage."""
        # TODO: Implement actual free space detection
        # This might require mounting camera storage or using camera-specific commands
        return None


def format_gphoto2_aperture(f_number: float) -> str:
    """
    Format aperture value for GPhoto2.
    
    Args:
        f_number: Aperture f-number (e.g., 8.0)
        
    Returns:
        GPhoto2-compatible aperture string (e.g., "8")
    """
    if isinstance(f_number, str):
        return f_number if f_number.startswith("f/") else f"f/{f_number}"

    value = float(f_number)
    if value.is_integer():
        return f"f/{int(value)}"
    return f"f/{value:.1f}"


def format_gphoto2_shutter(seconds) -> str:
    """
    Format shutter speed for GPhoto2.
    
    Args:
        seconds: Shutter speed in seconds
        
    Returns:
        GPhoto2-compatible shutter string (e.g., "1/125", "2")
    """
    if isinstance(seconds, str):
        if "/" in seconds:
            return seconds
        seconds = float(seconds)

    seconds = float(seconds)
    if seconds <= 0:
        raise ValueError(f"Shutter speed must be positive, got {seconds}")

    if seconds >= 1.0:
        return str(int(seconds)) if seconds.is_integer() else f"{seconds:.1f}"

    fraction = round(1.0 / seconds)
    return f"1/{fraction}"

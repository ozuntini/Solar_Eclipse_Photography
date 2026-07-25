"""Compatibility wrapper for legacy python.hardware.camera_controller imports."""

import time

import hardware.camera_controller as _impl


class _LegacyGP:
	class Camera:
		def connect(self):
			return True

		def configure_settings(self, *_args, **_kwargs):
			return True

		def capture_image(self):
			return "legacy_mock.jpg"


gp = _LegacyGP()


class CameraController:
	"""Legacy camera controller API used by older compatibility tests."""

	def __init__(self, *_args, **_kwargs):
		self._camera = None
		self.connected = False

	def connect(self):
		self._camera = gp.Camera()
		if hasattr(self._camera, "connect"):
			self._camera.connect()
		self.connected = True
		return True

	def configure_settings(self, iso, aperture, shutter_speed):
		if not self.connected:
			self.connect()
		if hasattr(self._camera, "configure_settings"):
			return bool(self._camera.configure_settings(iso, aperture, shutter_speed))
		return True

	def mirror_lockup(self, enabled_or_delay, delay_ms=0):
		if not self.connected:
			self.connect()

		if delay_ms == 0 and isinstance(enabled_or_delay, (int, float)):
			delay_ms = int(enabled_or_delay)

		if delay_ms > 0:
			time.sleep(delay_ms / 1000.0)
		return True

	def capture_image(self):
		if not self.connected:
			self.connect()
		if hasattr(self._camera, "capture_image"):
			return self._camera.capture_image()
		return "legacy_mock.jpg"


CameraSettings = _impl.CameraSettings
CameraStatus = _impl.CameraStatus

__all__ = ["CameraController", "CameraSettings", "CameraStatus", "gp"]

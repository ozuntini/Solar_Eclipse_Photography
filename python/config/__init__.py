"""Compatibility layer for legacy python.config imports."""

from .parser import ConfigParser, ConfigParserError, parse_config_file

__all__ = ["ConfigParser", "ConfigParserError", "parse_config_file"]

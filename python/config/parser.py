"""Compatibility parser wrapper for legacy import paths."""

from config.config_parser import ConfigParser, ConfigParserError, parse_config_file

__all__ = ["ConfigParser", "ConfigParserError", "parse_config_file"]

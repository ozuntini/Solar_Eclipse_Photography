"""Backward-compatible parser module.

This module keeps legacy imports working:
    from config.parser import ConfigParser
"""

from .config_parser import ConfigParser, ConfigParserError, parse_config_file

__all__ = ["ConfigParser", "ConfigParserError", "parse_config_file"]

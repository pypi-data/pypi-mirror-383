#####################################################################
#                                                                   #
# Frets on Fire                                                     #
# Copyright (C) 2006 Sami Kyöstilä                                  #
#                                                                   #
# This program is free software; you can redistribute it and/or     #
# modify it under the terms of the GNU General Public License       #
# as published by the Free Software Foundation; either version 2    #
# of the License, or (at your option) any later version.            #
#                                                                   #
# This program is distributed in the hope that it will be useful,   #
# but WITHOUT ANY WARRANTY; without even the implied warranty of    #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     #
# GNU General Public License for more details.                      #
#                                                                   #
# You should have received a copy of the GNU General Public License #
# along with this program; if not, write to the Free Software       #
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,        #
# MA  02110-1301, USA.                                              #
#####################################################################

import logging
import os
import sys
from pathlib import Path
from threading import RLock
from typing import Optional

from . import Resource

LOGGER_NAME = "fretsonfire"
DEFAULT_ENCODING = "utf-8"
DEFAULT_LOG_FILENAME = "fretsonfire.log"
NOTICE_LEVEL = logging.INFO + 5

logging.addLevelName(NOTICE_LEVEL, "NOTICE")

_logger = logging.getLogger(LOGGER_NAME)
_logger.setLevel(logging.DEBUG)

_config_lock = RLock()
_configured = False
_quiet = "-v" not in sys.argv
_current_log_path: Optional[Path] = None


def _determine_log_path(candidate: Optional[os.PathLike[str] | str]) -> Optional[Path]:
  if candidate:
    return Path(candidate)

  env_path = os.getenv("FRETSONFIRE_LOG_PATH")
  if env_path:
    return Path(env_path)

  try:
    writable_root = Path(Resource.getWritableResourcePath())
  except Exception:
    return None

  return writable_root / DEFAULT_LOG_FILENAME


def _build_console_handler(level: int) -> logging.Handler:
  handler = logging.StreamHandler()
  handler.setLevel(level)
  handler.setFormatter(logging.Formatter("(%(levelname).1s) %(message)s"))
  return handler


def _build_file_handler(path: Path, level: int) -> Optional[logging.Handler]:
  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(path, encoding=DEFAULT_ENCODING)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(asctime)s (%(levelname).1s) %(message)s"))
    return handler
  except OSError:
    return None


def configure(*, quiet: Optional[bool] = None, log_path: Optional[os.PathLike[str] | str] = None,
              level: int = logging.DEBUG, console: Optional[bool] = None) -> logging.Logger:
  """Configure the global logger.

  Args:
    quiet: Disable console logging when True.
    log_path: Explicit path to the logfile. Defaults to the writable resource directory.
    level: Logging level for handlers.
    console: Force console logging on or off. Overrides ``quiet`` if provided.
  """

  global _configured, _quiet, _current_log_path

  with _config_lock:
    if quiet is not None:
      _quiet = bool(quiet)

    use_console = console if console is not None else not _quiet

    if log_path is not None:
      target_path = _determine_log_path(log_path)
    else:
      target_path = _current_log_path or _determine_log_path(None)

    handlers: list[logging.Handler] = []

    if use_console:
      handlers.append(_build_console_handler(level))

    active_path: Optional[Path] = None

    if target_path is not None:
      file_handler = _build_file_handler(target_path, level)
      if file_handler is not None:
        handlers.append(file_handler)
        active_path = target_path

    if not handlers:
      handlers.append(logging.NullHandler())

    _logger.handlers.clear()
    for handler in handlers:
      _logger.addHandler(handler)

    _logger.setLevel(level)
    _configured = True
    _current_log_path = active_path

  return _logger


def _ensure_configured() -> None:
  if not _configured:
    configure()


def set_quiet(value: bool) -> None:
  """Enable or disable console logging."""
  configure(quiet=value)


def is_quiet() -> bool:
  return _quiet


def get_logger() -> logging.Logger:
  _ensure_configured()
  return _logger


def notice(msg, *args, **kwargs) -> None:
  _ensure_configured()
  _logger.log(NOTICE_LEVEL, msg, *args, **kwargs)


def debug(msg, *args, **kwargs) -> None:
  _ensure_configured()
  _logger.debug(msg, *args, **kwargs)


def warn(msg, *args, **kwargs) -> None:
  _ensure_configured()
  _logger.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs) -> None:
  _ensure_configured()
  _logger.error(msg, *args, **kwargs)


def warning(msg, *args, **kwargs) -> None:
  warn(msg, *args, **kwargs)


def info(msg, *args, **kwargs) -> None:
  _ensure_configured()
  _logger.info(msg, *args, **kwargs)

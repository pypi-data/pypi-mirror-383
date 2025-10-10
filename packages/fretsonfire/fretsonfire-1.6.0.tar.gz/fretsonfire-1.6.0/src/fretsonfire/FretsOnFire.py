#!/usr/bin/env python3
#####################################################################
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

"""
Main game executable.
"""
import argparse
import codecs
import os
import sys
from pathlib import Path

# Register the latin-1 encoding
import encodings.iso8859_1
import encodings.utf_8
codecs.register(lambda encoding: encodings.iso8859_1.getregentry())
codecs.register(lambda encoding: encodings.utf_8.getregentry())
assert codecs.lookup("iso-8859-1")
assert codecs.lookup("utf-8")

from .GameEngine import GameEngine
from .MainMenu import MainMenu
from . import Log
from . import Config
from . import Version

def parse_args(argv):
  parser = argparse.ArgumentParser(
    prog=Path(sys.argv[0]).name,
    add_help=True,
    description="Launch Frets on Fire",
  )
  parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="Verbose messages",
  )
  parser.add_argument(
    "-p", "--play",
    dest="song_name",
    metavar="songName",
    help="Start playing the given song",
  )
  return parser.parse_args(argv)

def main(argv=None):
  argv = list(sys.argv[1:] if argv is None else argv)
  args = parse_args(argv)

  if args.verbose:
    Log.set_quiet(False)

  song_name = args.song_name
  engine = None

  try:
    # Ensure Linux window managers associate the app window with its .desktop entry.
    if "DISPLAY" in os.environ and "SDL_VIDEO_X11_WMCLASS" not in os.environ:
      os.environ["SDL_VIDEO_X11_WMCLASS"] = Version.appName()

    while True:
      config = Config.load(Version.appName() + ".ini", setAsDefault = True)
      engine = GameEngine(config)
      menu   = MainMenu(engine, songName = song_name)
      engine.setStartupLayer(menu)

      try:
        while engine.run():
          pass
      except KeyboardInterrupt:
          pass

      if engine.restartRequested:
        Log.notice("Restarting.")

        try:
          # Determine whether we're running from an exe or not
          if hasattr(sys, "frozen"):
            if os.name == "nt":
              os.execl("FretsOnFire.exe", "FretsOnFire.exe", *sys.argv[1:])
            elif sys.platform == "darwin":
              # This exit code tells the launcher script to restart the game
              sys.exit(100)
            else:
              os.execl("./FretsOnFire", "./FretsOnFire", *sys.argv[1:])
          else:
            python_executable = sys.executable or "python3"
            script_path = Path(__file__).resolve()
            os.execl(python_executable, python_executable, str(script_path), *argv)
        except Exception as exc:
          Log.warn("Restart failed: %s" % exc)
          raise
        break
      else:
        break
  finally:
    if engine is not None:
      engine.quit()

  return 0

if __name__ == "__main__":
  sys.exit(main())

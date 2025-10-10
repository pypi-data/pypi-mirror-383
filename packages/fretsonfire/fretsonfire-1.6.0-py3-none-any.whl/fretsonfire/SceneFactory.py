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

# Scenes
import glob
import importlib
import sys

# Static list for now to ease building
#scenes = [n.replace(".py", "") for n in glob.glob("*Scene.py")]
scenes = ["GameResultsScene", "GuitarScene", "SongChoosingScene"]

def _import(name):
  """Import a scene module, preferring package-qualified imports."""
  if __package__:
    qualified_name = f"{__package__}.{name}"
    try:
      module = importlib.import_module(qualified_name)
    except ModuleNotFoundError as exc:
      if exc.name != qualified_name:
        raise
    else:
      globals()[name] = module
      sys.modules.setdefault(name, module)
      return module

  module = importlib.import_module(name)
  globals()[name] = module
  return module

def create(engine, name, owner, server = None, session = None, **args):
  assert session or server

  _import(name)

  m = globals()[name]
  if server:
    return getattr(m, name + "Server")(engine = engine, owner = owner, server = server, **args)
  else:
    return getattr(m, name + "Client")(engine = engine, owner = owner, session = session, **args)

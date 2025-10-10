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

import pygame
from pathlib import Path
from OpenGL.GL import glEnable
from OpenGL.GL.ARB.multisample import GL_MULTISAMPLE_ARB
from . import Log
from . import Version

class Video:
  def __init__(self, caption = "Game"):
    self.screen     = None
    self.caption    = caption
    self.fullscreen = False
    self.flags      = True
    self.multisamples = 0

  def setMode(self, resolution, fullscreen = False, flags = pygame.OPENGL | pygame.DOUBLEBUF,
              multisamples = 0):
    if fullscreen:
      flags |= pygame.FULLSCREEN
      
    target_flags = flags | pygame.FULLSCREEN if fullscreen else flags & ~pygame.FULLSCREEN

    try:    
      pygame.display.quit()
    except:
      pass
      
    pygame.display.init()

    try:
      icon_path = Path(Version.dataPath()) / "icon.png"
      pygame.display.set_icon(pygame.image.load(str(icon_path)))
    except Exception as error:
      Log.warn(f"Unable to apply window icon: {error}")

    pygame.display.gl_set_attribute(pygame.GL_RED_SIZE,   8)
    pygame.display.gl_set_attribute(pygame.GL_GREEN_SIZE, 8)
    pygame.display.gl_set_attribute(pygame.GL_BLUE_SIZE,  8)
    pygame.display.gl_set_attribute(pygame.GL_ALPHA_SIZE, 8)
      
    if multisamples:
      pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1);
      pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, multisamples);

    try:
      self.screen = pygame.display.set_mode(resolution, target_flags)
    except Exception as e:
      Log.error(str(e))
      if multisamples:
        Log.warn("Video setup failed. Trying without antialiasing.")
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 0);
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 0);
        multisamples = 0
        self.screen = pygame.display.set_mode(resolution, target_flags)
      else:
        Log.error("Video setup failed. Make sure your graphics card supports 32 bit display modes.")
        raise

    pygame.display.set_caption(self.caption)
    pygame.mouse.set_visible(False)

    if multisamples:
      try:
        glEnable(GL_MULTISAMPLE_ARB)
      except:
        pass

    self.flags        = target_flags
    self.fullscreen   = fullscreen
    self.multisamples = multisamples

    return bool(self.screen)
  
  def toggleFullscreen(self):
    assert self.screen

    resolution = self.screen.get_size()
    previous_flags = self.flags
    previous_fullscreen = self.fullscreen
    previous_multisamples = self.multisamples

    fullscreen = not previous_fullscreen

    flags = previous_flags
    if fullscreen:
      flags |= pygame.FULLSCREEN
    else:
      flags &= ~pygame.FULLSCREEN

    try:
      return bool(self.setMode(resolution, fullscreen = fullscreen,
                               flags = flags, multisamples = previous_multisamples))
    except Exception as error:
      Log.warn(f"Unable to toggle fullscreen: {error}")
      try:
        self.setMode(resolution, fullscreen = previous_fullscreen,
                     flags = previous_flags, multisamples = previous_multisamples)
      except Exception:
        pass
      return False

  def flip(self):
    pygame.display.flip()

  def getVideoModes(self):
    return pygame.display.list_modes()

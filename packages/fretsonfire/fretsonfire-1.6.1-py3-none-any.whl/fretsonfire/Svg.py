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

from __future__ import annotations

from io import BytesIO
from math import cos, sin
from typing import Optional, Tuple

from OpenGL.GL import *
from PIL import Image

from . import Config, Log
from .Texture import Texture

import skia

# Rendering quality is expressed as an upscaling factor before downsampling.
LOW_QUALITY = 0
NORMAL_QUALITY = 1
HIGH_QUALITY = 2

_RENDER_SCALE = {
  LOW_QUALITY: 1.0,
  NORMAL_QUALITY: 1.0,
  HIGH_QUALITY: 2.0,
}

Config.define("opengl", "svgquality", int, NORMAL_QUALITY)


def _matrix_multiply(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
  return [
    [
      a[i][0] * b[0][j] + a[i][1] * b[1][j] + a[i][2] * b[2][j]
      for j in range(3)
    ]
    for i in range(3)
  ]


class SvgTransform:
  def __init__(self, base_transform: Optional[SvgTransform] = None):
    self.matrix = [[1.0, 0.0, 0.0],
                   [0.0, 1.0, 0.0],
                   [0.0, 0.0, 1.0]]
    if base_transform:
      self.matrix = [row[:] for row in base_transform.matrix]

  def reset(self) -> None:
    self.matrix = [[1.0, 0.0, 0.0],
                   [0.0, 1.0, 0.0],
                   [0.0, 0.0, 1.0]]

  def translate(self, dx: float, dy: float) -> None:
    translation = [[1.0, 0.0, dx],
                   [0.0, 1.0, dy],
                   [0.0, 0.0, 1.0]]
    self.matrix = _matrix_multiply(self.matrix, translation)

  def rotate(self, angle: float) -> None:
    c = cos(angle)
    s = sin(angle)
    rotation = [[c, -s, 0.0],
                [s,  c, 0.0],
                [0.0, 0.0, 1.0]]
    self.matrix = _matrix_multiply(self.matrix, rotation)

  def scale(self, sx: float, sy: float) -> None:
    scaling = [[sx, 0.0, 0.0],
               [0.0, sy, 0.0],
               [0.0, 0.0, 1.0]]
    self.matrix = _matrix_multiply(self.matrix, scaling)

  def transform(self, other: SvgTransform) -> None:
    self.matrix = _matrix_multiply(self.matrix, other.matrix)

  def applyGL(self) -> None:
    m = self.matrix
    gl_mult = [
      m[0][0], m[1][0], 0.0, 0.0,
      m[0][1], m[1][1], 0.0, 0.0,
      0.0,     0.0,     1.0, 0.0,
      m[0][2], m[1][2], 0.0, 1.0,
    ]
    glMultMatrixf(gl_mult)


class SvgContext:
  def __init__(self, geometry: Tuple[int, int, int, int]):
    self.geometry = geometry
    self.transform = SvgTransform()
    self._render_quality = NORMAL_QUALITY
    self.setGeometry(geometry)
    self.setProjection(geometry)
    try:
      glMatrixMode(GL_MODELVIEW)
    except Exception:  # pragma: no cover - OpenGL availability guard
      Log.warn(
        "SVG renderer initialization failed; expect corrupted graphics. "
        "Upgrade OpenGL drivers and verify 32-bit color precision."
      )

  def setGeometry(self, geometry: Optional[Tuple[int, int, int, int]] = None) -> None:
    if geometry:
      self.geometry = geometry
    x, y, w, h = self.geometry
    glViewport(int(x), int(y), int(w), int(h))
    self.transform.reset()
    if w and h:
      self.transform.scale(w / 640.0, h / 480.0)

  def setProjection(self, geometry: Optional[Tuple[int, int, int, int]] = None) -> None:
    geometry = geometry or self.geometry
    x, y, w, h = geometry
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(x, x + w, y, y + h, -100, 100)
    glMatrixMode(GL_MODELVIEW)
    self.geometry = geometry

  def setRenderingQuality(self, quality: int) -> None:
    if quality not in (LOW_QUALITY, NORMAL_QUALITY, HIGH_QUALITY):
      Log.warn("Unknown SVG rendering quality %s; keeping previous value", quality)
      return
    self._render_quality = quality

  def getRenderingQuality(self) -> int:
    return self._render_quality

  def _render_scale(self) -> float:
    return _RENDER_SCALE.get(self._render_quality, 1.0)

  def clear(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 0.0) -> None:
    glDepthMask(True)
    glEnable(GL_COLOR_MATERIAL)
    glClearColor(r, g, b, a)
    glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


class SvgDrawing:
  def __init__(self, context: SvgContext, svg_data):
    self.context = context
    self.transform = SvgTransform()
    self.texture: Optional[Texture] = None
    self._dom: Optional["skia.SVGDOM"] = None
    self._intrinsic_size: Optional[Tuple[int, int]] = None
    self._source_path: Optional[str] = None

    svg_bytes: Optional[bytes] = None
    if hasattr(svg_data, "read"):
      svg_bytes = svg_data.read()
    elif isinstance(svg_data, str):
      self._source_path = svg_data
      lower = svg_data.lower()
      if lower.endswith(".png"):
        self.texture = Texture(svg_data)
      elif lower.endswith(".svg"):
        with open(svg_data, "rb") as handle:
          svg_bytes = handle.read()
      else:
        # Assume this is a bitmap resource that Texture can handle directly.
        self.texture = Texture(svg_data)
    else:
      raise RuntimeError("Unsupported SVG input type: %r" % (type(svg_data),))

    if svg_bytes is not None:
      self._load_dom(svg_bytes)

    if not self.texture and not self._dom:
      source = self._source_path or "inline SVG"
      raise RuntimeError(f"Unable to load texture or SVG data from {source}.")

  def _load_dom(self, svg_bytes: bytes) -> None:
    stream = skia.MemoryStream.MakeCopy(svg_bytes)
    dom = skia.SVGDOM.MakeFromStream(stream)
    if dom is None:
      source = self._source_path or "inline SVG"
      raise RuntimeError(f"Failed to parse SVG resource: {source}")
    self._dom = dom
    size = dom.containerSize()
    width = int(round(size.width())) if size.width() > 0 else None
    height = int(round(size.height())) if size.height() > 0 else None
    if width and height:
      self._intrinsic_size = (max(1, width), max(1, height))
    else:
      self._intrinsic_size = None

  def _default_texture_size(self) -> Tuple[int, int]:
    if self.texture:
      return tuple(int(v) for v in self.texture.pixelSize)
    if self._intrinsic_size:
      return self._intrinsic_size
    _, _, w, h = self.context.geometry
    return (max(1, int(w)), max(1, int(h)))

  def _render_svg_to_image(self, width: int, height: int) -> Image.Image:
    assert self._dom is not None
    scale = self.context._render_scale()
    render_width = max(1, int(round(width * scale)))
    render_height = max(1, int(round(height * scale)))

    self._dom.setContainerSize(skia.Size(float(render_width), float(render_height)))
    surface = skia.Surface.MakeRasterN32Premul(render_width, render_height)
    if surface is None:
      raise RuntimeError("Unable to allocate Skia surface for SVG rendering")
    canvas = surface.getCanvas()
    canvas.clear(skia.Color4f(0.0, 0.0, 0.0, 0.0))
    self._dom.render(canvas)
    image = surface.makeImageSnapshot()
    if image is None:
      raise RuntimeError("Unable to snapshot rendered SVG surface")
    data = image.encodeToData()
    if data is None:
      raise RuntimeError("Unable to encode rendered SVG to image data")

    with BytesIO(bytes(data)) as encoded:
      pil_image = Image.open(encoded)
      pil_image.load()
    if pil_image.mode != "RGBA":
      pil_image = pil_image.convert("RGBA")

    if scale != 1.0:
      pil_image = pil_image.resize((width, height), Image.LANCZOS)

    return pil_image

  def convertToTexture(self, width: int, height: int) -> None:
    if self.texture and (self.texture.pixelSize == (width, height) or not self._dom):
      return
    if not self._dom:
      raise RuntimeError("SVG drawing does not contain vector data to render")
    image = self._render_svg_to_image(width, height)
    texture = Texture()
    texture.loadImage(image)
    self.texture = texture

  def _ensure_texture(self) -> None:
    if self.texture:
      return
    width, height = self._default_texture_size()
    self.convertToTexture(width, height)

  def _get_effective_transform(self) -> SvgTransform:
    transform = SvgTransform(self.transform)
    transform.transform(self.context.transform)
    return transform

  def draw(self, color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)) -> None:
    self._ensure_texture()
    if not self.texture:
      raise RuntimeError("SVG drawing has no texture to draw")

    glMatrixMode(GL_TEXTURE)
    glPushMatrix()
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    self.context.setProjection()
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()

    transform = self._get_effective_transform()
    glLoadIdentity()
    transform.applyGL()

    glScalef(self.texture.pixelSize[0], self.texture.pixelSize[1], 1)
    glTranslatef(-0.5, -0.5, 0)
    glColor4f(*color)

    self.texture.bind()
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0.0, 1.0)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(1.0, 1.0)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0.0, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(1.0, 0.0)
    glEnd()
    glDisable(GL_TEXTURE_2D)

    glMatrixMode(GL_TEXTURE)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

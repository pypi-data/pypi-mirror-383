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

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Tuple
from xml.etree import ElementTree as ET

COLLADA_NS = "http://www.collada.org/2005/11/COLLADASchema"
_NS = f"{{{COLLADA_NS}}}"


def _tag(name: str) -> str:
  return f"{_NS}{name}"


def _strip(tag: str) -> str:
  if tag.startswith("{"):
    return tag.split("}", 1)[1]
  return tag


def _floats(text: Optional[str]) -> List[float]:
  if not text:
    return []
  return [float(value) for value in text.split()]


def _ints(text: Optional[str]) -> List[int]:
  if not text:
    return []
  return [int(value) for value in text.split()]


@dataclass
class FloatArray:
  data: List[float]


@dataclass
class DaeAccessor:
  stride: int
  count: int


@dataclass
class DaeTechniqueCommon:
  accessor: DaeAccessor


@dataclass
class DaeSource:
  id: str
  source: FloatArray
  techniqueCommon: DaeTechniqueCommon


@dataclass
class DaeInput:
  semantic: str
  source: str
  offset: int = 0
  set: Optional[int] = None


@dataclass
class DaeVertices:
  inputs: List[DaeInput]

  def FindInput(self, semantic: str) -> Optional[DaeInput]:
    for entry in self.inputs:
      if entry.semantic == semantic:
        return entry
    return None


@dataclass
class DaePrimitive:
  inputs: List[DaeInput]
  polygons: List[List[int]] = field(default_factory=list)
  triangles: List[int] = field(default_factory=list)
  material: Optional[str] = None


@dataclass
class DaeMesh:
  sources: Dict[str, DaeSource]
  vertices: DaeVertices
  primitives: List[DaePrimitive]

  def FindSource(self, input_desc: Optional[DaeInput]) -> Optional[DaeSource]:
    if input_desc is None:
      return None
    return self.sources.get(input_desc.source)


@dataclass
class DaeGeometry:
  id: str
  name: str
  data: Optional[DaeMesh]


@dataclass
class DaeLightTechnique:
  type: str
  color: Tuple[float, float, float, float]


@dataclass
class DaeLight:
  id: str
  name: str
  techniqueCommon: DaeLightTechnique


@dataclass
class DaeGeometryInstance:
  object: Optional[DaeGeometry]
  bindMaterials: List[object] = field(default_factory=list)


@dataclass
class DaeLightInstance:
  object: Optional[DaeLight]


@dataclass
class DaeNode:
  id: str
  name: str
  transforms: List[Tuple[str, List[float]]]
  iGeometries: List[DaeGeometryInstance] = field(default_factory=list)
  iLights: List[DaeLightInstance] = field(default_factory=list)
  nodes: List['DaeNode'] = field(default_factory=list)


@dataclass
class DaeVisualScene:
  id: str
  name: str
  nodes: List[DaeNode]


class DaeLibrary:
  def __init__(self) -> None:
    self.items: List[object] = []
    self._index: Dict[str, object] = {}

  def clear(self) -> None:
    self.items.clear()
    self._index.clear()

  def add(self, item: object) -> None:
    identifier = getattr(item, "id", None)
    if identifier:
      self._index[identifier] = item
    self.items.append(item)

  def FindObject(self, object_id: str) -> Optional[object]:
    return self._index.get(object_id)

  def __iter__(self) -> Iterator[object]:
    return iter(self.items)


class DaeDocument:
  def __init__(self) -> None:
    self.version = ""
    self.xmlns = COLLADA_NS
    self.geometriesLibrary = DaeLibrary()
    self.lightsLibrary = DaeLibrary()
    self.visualScenesLibrary = DaeLibrary()

  def LoadDocumentFromFile(self, filename: str) -> None:
    tree = ET.parse(filename)
    root = tree.getroot()
    self.version = root.attrib.get("version", "")
    if root.tag.startswith("{"):
      self.xmlns = root.tag.split("}", 1)[0][1:]

    self._parse_geometries(root.find(_tag("library_geometries")))
    self._parse_lights(root.find(_tag("library_lights")))
    self._parse_visual_scenes(root.find(_tag("library_visual_scenes")))

  # ------------------------------------------------------------------
  # Parsing helpers
  # ------------------------------------------------------------------

  def _parse_geometries(self, library_elem: Optional[ET.Element]) -> None:
    self.geometriesLibrary.clear()
    if library_elem is None:
      return

    for geom_elem in library_elem.findall(_tag("geometry")):
      geom_id = geom_elem.attrib.get("id", "")
      name = geom_elem.attrib.get("name", geom_id)
      mesh_elem = geom_elem.find(_tag("mesh"))
      mesh = self._parse_mesh(mesh_elem) if mesh_elem is not None else None
      self.geometriesLibrary.add(DaeGeometry(id=geom_id, name=name, data=mesh))

  def _parse_mesh(self, mesh_elem: ET.Element) -> DaeMesh:
    sources: Dict[str, DaeSource] = {}
    for source_elem in mesh_elem.findall(_tag("source")):
      parsed = self._parse_source(source_elem)
      sources[parsed.id] = parsed

    vertices_elem = mesh_elem.find(_tag("vertices"))
    vertices = self._parse_vertices(vertices_elem)

    primitives: List[DaePrimitive] = []
    for tag in ("polygons", "triangles"):
      for prim_elem in mesh_elem.findall(_tag(tag)):
        primitives.append(self._parse_primitive(prim_elem, tag))

    for polylist_elem in mesh_elem.findall(_tag("polylist")):
      primitives.extend(self._parse_polylist(polylist_elem))

    return DaeMesh(sources=sources, vertices=vertices, primitives=primitives)

  def _parse_source(self, source_elem: ET.Element) -> DaeSource:
    source_id = source_elem.attrib.get("id", "")
    float_array_elem = source_elem.find(_tag("float_array"))
    float_values = _floats(float_array_elem.text if float_array_elem is not None else "")

    accessor_elem = source_elem.find(_tag("technique_common"))
    accessor_node = accessor_elem.find(_tag("accessor")) if accessor_elem is not None else None
    stride = int(accessor_node.attrib.get("stride", "1")) if accessor_node is not None else 1
    count = int(accessor_node.attrib.get("count", str(len(float_values) // stride))) if accessor_node is not None else len(float_values) // stride

    return DaeSource(
      id=source_id,
      source=FloatArray(float_values),
      techniqueCommon=DaeTechniqueCommon(accessor=DaeAccessor(stride=stride, count=count)),
    )

  def _parse_vertices(self, vertices_elem: Optional[ET.Element]) -> DaeVertices:
    if vertices_elem is None:
      return DaeVertices(inputs=[])
    inputs = [self._parse_input(input_elem) for input_elem in vertices_elem.findall(_tag("input"))]
    return DaeVertices(inputs=inputs)

  def _parse_input(self, input_elem: ET.Element) -> DaeInput:
    semantic = input_elem.attrib.get("semantic", "")
    source = input_elem.attrib.get("source", "")
    if source.startswith("#"):
      source = source[1:]
    offset = int(input_elem.attrib.get("offset", "0"))
    set_attr = input_elem.attrib.get("set")
    set_value = int(set_attr) if set_attr is not None else None
    return DaeInput(semantic=semantic, source=source, offset=offset, set=set_value)

  def _parse_primitive(self, prim_elem: ET.Element, prim_type: str) -> DaePrimitive:
    inputs = [self._parse_input(input_elem) for input_elem in prim_elem.findall(_tag("input"))]
    material = prim_elem.attrib.get("material")
    if prim_type == "triangles":
      indices: List[int] = []
      for p_elem in prim_elem.findall(_tag("p")):
        indices.extend(_ints(p_elem.text))
      return DaePrimitive(inputs=inputs, triangles=indices, material=material)

    polygons = [_ints(p_elem.text) for p_elem in prim_elem.findall(_tag("p"))]
    return DaePrimitive(inputs=inputs, polygons=polygons, material=material)

  def _parse_polylist(self, polylist_elem: ET.Element) -> List[DaePrimitive]:
    inputs = [self._parse_input(input_elem) for input_elem in polylist_elem.findall(_tag("input"))]
    vcount = _ints(polylist_elem.findtext(_tag("vcount")))
    indices = _ints(polylist_elem.findtext(_tag("p")))
    if not vcount:
      return []

    stride = max((input_desc.offset for input_desc in inputs), default=0) + 1
    cursor = 0
    polygons: List[List[int]] = []
    for count in vcount:
      size = count * stride
      polygons.append(indices[cursor:cursor + size])
      cursor += size

    return [DaePrimitive(inputs=inputs, polygons=polygons, material=polylist_elem.attrib.get("material"))]

  def _parse_lights(self, library_elem: Optional[ET.Element]) -> None:
    self.lightsLibrary.clear()
    if library_elem is None:
      return

    for light_elem in library_elem.findall(_tag("light")):
      light_id = light_elem.attrib.get("id", "")
      name = light_elem.attrib.get("name", light_id)
      technique_common = light_elem.find(_tag("technique_common"))
      technique = self._parse_light_technique(technique_common)
      self.lightsLibrary.add(DaeLight(id=light_id, name=name, techniqueCommon=technique))

  def _parse_light_technique(self, tc_elem: Optional[ET.Element]) -> DaeLightTechnique:
    if tc_elem is None:
      return DaeLightTechnique(type="ambient", color=(1.0, 1.0, 1.0, 1.0))

    for child in tc_elem:
      light_type = _strip(child.tag)
      color_elem = child.find(_tag("color"))
      values = _floats(color_elem.text if color_elem is not None else None)
      if len(values) == 3:
        values.append(1.0)
      elif not values:
        values = [1.0, 1.0, 1.0, 1.0]
      return DaeLightTechnique(type=light_type, color=tuple(values[:4]))

    return DaeLightTechnique(type="ambient", color=(1.0, 1.0, 1.0, 1.0))

  def _parse_visual_scenes(self, library_elem: Optional[ET.Element]) -> None:
    self.visualScenesLibrary.clear()
    if library_elem is None:
      return

    for scene_elem in library_elem.findall(_tag("visual_scene")):
      scene_id = scene_elem.attrib.get("id", "")
      name = scene_elem.attrib.get("name", scene_id)
      nodes = [self._parse_node(node_elem) for node_elem in scene_elem.findall(_tag("node"))]
      self.visualScenesLibrary.add(DaeVisualScene(id=scene_id, name=name, nodes=nodes))

  def _parse_node(self, node_elem: ET.Element) -> DaeNode:
    node_id = node_elem.attrib.get("id", "")
    name = node_elem.attrib.get("name", node_id)

    transforms: List[Tuple[str, List[float]]] = []
    for tag in ("translate", "rotate", "scale", "matrix", "lookat"):
      for trans_elem in node_elem.findall(_tag(tag)):
        transforms.append((tag, _floats(trans_elem.text)))

    i_geometries: List[DaeGeometryInstance] = []
    for inst_elem in node_elem.findall(_tag("instance_geometry")):
      target = inst_elem.attrib.get("url", "")
      if target.startswith("#"):
        target = target[1:]
      geometry = self.geometriesLibrary.FindObject(target)
      i_geometries.append(DaeGeometryInstance(object=geometry))

    i_lights: List[DaeLightInstance] = []
    for inst_elem in node_elem.findall(_tag("instance_light")):
      target = inst_elem.attrib.get("url", "")
      if target.startswith("#"):
        target = target[1:]
      light = self.lightsLibrary.FindObject(target)
      i_lights.append(DaeLightInstance(object=light))

    child_nodes = [self._parse_node(child) for child in node_elem.findall(_tag("node"))]

    return DaeNode(
      id=node_id,
      name=name,
      transforms=transforms,
      iGeometries=i_geometries,
      iLights=i_lights,
      nodes=child_nodes,
    )


__all__ = [
  "DaeAccessor",
  "DaeDocument",
  "DaeGeometry",
  "DaeGeometryInstance",
  "DaeInput",
  "DaeLight",
  "DaeLightInstance",
  "DaeLightTechnique",
  "DaeLibrary",
  "DaeMesh",
  "DaeNode",
  "DaePrimitive",
  "DaeSource",
  "DaeTechniqueCommon",
  "DaeVertices",
  "DaeVisualScene",
  "FloatArray",
]

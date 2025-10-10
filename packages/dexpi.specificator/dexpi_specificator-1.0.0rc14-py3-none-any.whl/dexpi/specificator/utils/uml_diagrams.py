
# pylint: disable=missing-docstring

from __future__ import annotations

import hashlib
import itertools
import json
import operator
import pathlib
import platform
import re
import shutil
import subprocess
import tempfile
import typing as T
import unicodedata

from attrs import define
from lxml import etree
from pnb.mcl.metamodel import standard as metamodel

THIS_DIR = pathlib.Path(__file__).parent

ELK_JS_DIR = THIS_DIR / 'uml_diagrams_js'
NODE_MODULES_DIR = ELK_JS_DIR / 'node_modules'

NODE_PATH = 'node'
NPM_PATH = 'npm'

def check_dependencies():
    
    if NODE_MODULES_DIR.is_dir():
        return

    if platform.system() == 'Windows':
        use_shell = True
    elif platform.system() == 'Linux':
        use_shell = False
    else:
        raise EnvironmentError(f'unknown system: {platform.system()}')

    p = subprocess.Popen(
        [NPM_PATH, 'install'],
        cwd=ELK_JS_DIR,
        shell=use_shell)
    
    if p.wait():
        shutil.rmtree(NODE_MODULES_DIR, ignore_errors=True)
        raise EnvironmentError('installation of node modules failed')
        

class XmlNamespace(str):

    def __new__(cls, value: str):
        namespace = super().__new__(cls, value)
        namespace.__term_prefix = f'{{{value}}}' if value else ''
        return namespace

    def term(self, name: str):
        return self.__term_prefix + name

    def __getattr__(self, name):
        return self.term(name)
    


SVG = XmlNamespace('http://www.w3.org/2000/svg')


NBSP = unicodedata.lookup('NBSP')

LinkGetter = T.Callable[[metamodel.Element, ], T.Optional[str]]

EPS = 1e-6



class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
        
    def __repr__(self):
        return f'<{self.x}, {self.y}>'
    
Font = T.Literal['normal', 'element']
FontSize = T.Literal['normal', 'large']

@define(eq=False)
class Text:
    text: str
    font: Font
    font_size: FontSize
    link: T.Optional[str]=None
    bold: bool=False
    italic: bool=False
    underlined: bool=False
    
    
Alignment = T.Literal['left', 'center']

LineStyle = T.Literal['solid', 'short_dash']

@define
class Cell:
    alignment: Alignment
    parts: list[Text] # TODO rename texts

    def iter_texts(self) -> T.Iterator[Text]:
        yield from self.parts

    def get_size(self, renderer):
        width = 0
        height = 0
        for text in self.parts:
            text_width, text_height = renderer.get_text_size(text)
            width += text_width
            height = max(height, text_height)
        return width, height
    
    def render(self, renderer, origo, width):
        renderer.draw_texts(
            origo,
            width,
            self.alignment,
            self.parts)
    

@define
class Row:
    cells: list[Cell]
    
    def iter_texts(self) -> T.Iterator[Text]:
        return itertools.chain.from_iterable(cell.iter_texts() for cell in self.cells)

    def get_cell_sizes(self, renderer):
        return [cell.get_size(renderer) for cell in self.cells]
    
class Section:
    
    def iter_texts(self) -> T.Iterator[Text]:
        raise NotImplementedError()
    
    def get_size(self, renderer):
        raise NotImplementedError()

@define
class Table(Section):
    rows: list[Row]
    
    col_spacing = 3
    
    def iter_texts(self) -> T.Iterator[Text]:
        return itertools.chain.from_iterable(row.iter_texts() for row in self.rows)
    
    def get_col_and_row_dimensions(self, renderer): # TODO: rename to "min"
        
        col_widths = []
        row_heights = []

        for row in self.rows:
            cell_sizes = row.get_cell_sizes(renderer)
            col_widths = [
                max(col_width if col_width else 0., cell_size[0] if cell_size else 0.)
                for (col_width, cell_size)
                in itertools.zip_longest(col_widths, cell_sizes)]
            if cell_sizes:
                row_height = max(cell_size[1] for cell_size in cell_sizes)
            else:
                row_height = 0.
            row_heights.append(row_height)
            
        return col_widths, row_heights
        
    
    def get_size(self, renderer):
        
        col_widths, row_heights = self.get_col_and_row_dimensions(renderer)

        if col_widths:
            width = sum(col_widths) + (len(col_widths)-1) * self.col_spacing
        else:
            width = 0.
            
        if row_heights:
            height = sum(row_heights)
        else:
            height = 0.
        
        return width, height
    
    def render(self, renderer, origo, width, owner_width):

        col_widths, row_heights = self.get_col_and_row_dimensions(renderer)
        if not col_widths or not row_heights:
            return
        
        assert sum(col_widths) <= width + EPS
        # Auto-expand last col to get full required width.
        col_widths[-1] = max(width - sum(col_widths[:-1]), 0.)
        
        y = origo.y
        
        for row, row_height in zip(self.rows, row_heights):
            x = origo.x
            for cell, col_width in zip(row.cells, col_widths):
                cell.render(renderer, Point(x, y), col_width)
                x += col_width + self.col_spacing
            y += row_height


            

@define
class Separator(Section):

    def iter_texts(self) -> T.Iterator[Text]:
        return ()
    
    def get_size(self, renderer):
        return 0., 1.
    
    def render(self, renderer, origo, width, owner_width):

        renderer.draw_line([
            Point(origo.x - 0.5*(owner_width-width), origo.y),
            Point(origo.x + 0.5*(owner_width+width), origo.y)])


class DiagramItem:

    def on_add(self, specification: DiagramSpecification) -> None:
        pass
    
    def iter_texts(self) -> T.Iterator[Text]:
        raise NotImplementedError()        

    def elk_source(self, item_id: str, specification: DiagramSpecification, renderer: Renderer) -> tuple[dict[str, str], dict, dict]:
        raise NotImplementedError()
        
    layout: T.Callable


class ItemLayout:
    pass




BackgroundColor = T.Literal['type', 'main_type', 'instance', 'background', 'foreground']



@define(eq=False)
class Box(DiagramItem):
    background_color: BackgroundColor
    padding: float
    frame: bool
    sections: list[Section]
    top_right_table: T.Optional[Table] = None

    def iter_texts(self) -> T.Iterator[Text]:
        for section in self.sections:
            yield from section.iter_texts()
        if self.top_right_table:
            yield from self.top_right_table.iter_texts()
            

    def iter_section_origos(self, renderer, origo):
        x = origo.x + self.padding
        y = origo.y + self.padding
        for section in self.sections:
            yield Point(x, y)
            section_width, section_height = section.get_size(renderer)
            y += section.get_size(renderer)[1] + self.padding

    def elk_source(self, item_id: str, specification: DiagramSpecification, renderer: Renderer):
        width = 0.
        height = 0.
        for section in self.sections:
            section_width, section_height = section.get_size(renderer)
            width = max(width, section_width)
            height += section_height
        width += 2*self.padding                       # left and right
        height += (len(self.sections)+1)*self.padding # top and bottom and between sections
        
        if self.top_right_table:
            tr_table_width, tr_table_height = self.top_right_table.get_size(renderer)
     
            tr_table_width += 2*self.padding
            tr_table_height += 2*self.padding
            
            # Ensure box is significantly wider than top-right table.
            width = max(width, tr_table_width+10*self.padding)
            height += tr_table_height
            

        connectors = max(
            specification.top_connectors_by_item.get(self, 0),
            specification.bottom_connectors_by_item.get(self, 0))
        min_width_for_connectors = connectors * 50
        width = max(width, min_width_for_connectors)

        return (
            {item_id: 'box_data'},
            [dict( id=item_id, width=width, height=height)],
            [])

    def layout(self, box_data):
        return BoxLayout(
            self,
            Point(float(box_data['x']), float(box_data['y'])),
            float(box_data['width']),
            float(box_data['height']))


@define
class BoxLayout(ItemLayout):
    box: Box
    position: Point
    width: width
    height: height
    
    def render(self, renderer):
        renderer.draw_box(
            self.position,
            self.width,
            self.height,
            frame=self.box.frame,
            background_color=self.box.background_color)
        
        section_width = self.width - 2*self.box.padding
        sections_origo = self.position

        if self.box.top_right_table:
            tr_table_width, tr_table_height = self.box.top_right_table.get_size(renderer)
            tr_table_width_padded = tr_table_width + 2*self.box.padding
            tr_table_height_padded = tr_table_height + 2*self.box.padding

            renderer.draw_line(
                points=[
                    Point(
                        self.position.x + self.width - tr_table_width_padded,
                        self.position.y),
                    Point(
                        self.position.x + self.width - tr_table_width_padded,
                        self.position.y + tr_table_height_padded),
                    Point(
                        self.position.x + self.width,
                        self.position.y + tr_table_height_padded)],
                line_style='short_dash')

            self.box.top_right_table.render(
                renderer,
                Point(
                    self.position.x + self.width - (tr_table_width + self.box.padding),
                    self.position.y + self.box.padding),
                tr_table_width,
                tr_table_width+2*self.box.padding)

            sections_origo = Point(sections_origo.x, sections_origo.y + tr_table_height_padded)

        for section, section_origo in zip(
                self.box.sections, self.box.iter_section_origos(renderer, sections_origo)):
            section.render(renderer, section_origo, section_width, self.width)



LineMarker = T.Literal['closed_arrow', 'filled_diamond', 'open_arrow']

@define(eq=False)
class Line(DiagramItem):
    source_id: str
    target_id: str
    label_box: T.Optional[Box] = None
    source_label: T.Optional[str] = None
    source_marker: T.Optional[LineMarker] = None
    target_label: T.Optional[str] = None
    target_marker: T.Optional[LineMarker] = None
    line_style: short_dtyle = 'solid'
    

    def on_add(self, specification: DiagramSpecification) -> None:
        source_item = specification.item_by_id.get(self.source_id)
        assert source_item
        specification.bottom_connectors_by_item[source_item] = specification.bottom_connectors_by_item.get(source_item, 0) + 1
        target_item = specification.item_by_id.get(self.target_id)
        assert target_item
        specification.top_connectors_by_item[target_item] = specification.top_connectors_by_item.get(target_item, 0) + 1
    
    def iter_texts(self) -> T.Iterator[Text]:
        
        
        # TODO: merge with elk source
        yield Text(
            text=self.source_label or '.',
            font='normal',
            font_size='normal')
        yield Text(
            text=self.target_label or '.',
            font='normal',
            font_size='normal')
        if self.label_box:
            yield from self.label_box.iter_texts()

        
        return [] # TODO

    def elk_source(self, item_id: str, specification: DiagramSpecification, renderer: Renderer):
        
        label_box_id = f'{item_id}-label-box'
        source_to_aux_edge_id = f'{item_id}-from'
        aux_to_target_edge_id = f'{item_id}-to'
        
        id_mapping = {
            label_box_id: 'label_box_data',
            source_to_aux_edge_id: 'source_to_aux_edge_data',
            aux_to_target_edge_id: 'aux_to_target_edge_data'}
        
        if self.label_box:
            label_box_id_mapping, label_box_children, label_box_edges = self.label_box.elk_source(
                label_box_id, specification, renderer)
            assert len(label_box_id_mapping) == 1
            assert label_box_id_mapping[label_box_id] == 'box_data'
            assert len(label_box_children) == 1
            assert not label_box_edges
            label_box_data = label_box_children[0]
        else:
            label_box_data = dict(id=label_box_id, width=1, height=1)

        source_to_aux_edge_data = dict(
            id=source_to_aux_edge_id,
            sources=[self.source_id],
            targets=[label_box_id])
        source_label_width, source_label_height = renderer.get_text_size(Text(
            text=self.source_label or '.',
            font='normal',
            font_size='normal'))
        source_to_aux_edge_data['labels'] = [{
            'text': '.',
            'layoutOptions': { 'edgeLabels.placement': 'TAIL'},
            'width': 1,
            'height': source_label_height}]

        aux_to_target_edge_data = dict(
            id=aux_to_target_edge_id,
            sources=[label_box_id],
            targets=[self.target_id])
        target_label_width, target_label_height = renderer.get_text_size(Text(
            text=self.target_label or '.',
            font='normal',
            font_size='normal'))
        aux_to_target_edge_data['labels'] = [{
            'text': '.',
            'layoutOptions': { 'edgeLabels.placement': 'HEAD'},
            'width': 1,
            'height': target_label_height}]

        return (
            id_mapping,
            [label_box_data],
            [source_to_aux_edge_data, aux_to_target_edge_data])
        
    def layout(self, label_box_data, source_to_aux_edge_data, aux_to_target_edge_data) -> LineLayout:

        # TODO: move below

        def point_from_data(data):
            return Point(float(data['x']), float(data['y']))

        def points_from_sections(data: dict):
            sections = data.get('sections')
            assert isinstance(sections, list)
            assert len(sections) == 1
            section = sections[0]
            points = [point_from_data(section.get('startPoint'))]
            bend_points_data = section.get('bendPoints')
            if bend_points_data:
                assert isinstance(bend_points_data, list)
                points.extend(point_from_data(point_data) for point_data in bend_points_data)
            points.append(point_from_data(section.get('endPoint')))
            return cleaned_points(points)

        def cleaned_points(points):
            return points

        if self.label_box:
            label_box_layout = self.label_box.layout(label_box_data)
        else:
            label_box_layout = None

        if self.source_label:
            source_label_position = (
                point_from_data(source_to_aux_edge_data['labels'][0]) + Point(5, 1.5))
        else:
            source_label_position = None

        if self.target_label:
            target_label_position = (
                point_from_data(aux_to_target_edge_data['labels'][0]) + Point(5, 1.5))
        else:
            target_label_position = None

        return LineLayout(
            self,
            label_box_layout=label_box_layout,
            source_to_aux_points=points_from_sections(source_to_aux_edge_data),
            aux_to_target_points = points_from_sections(aux_to_target_edge_data),
            source_label_position=source_label_position,
            target_label_position=target_label_position)


@define
class LineLayout(ItemLayout):
    line: Line
    label_box_layout: T.Optional[BoxLayout]
    source_to_aux_points: list[Point]
    aux_to_target_points: list[Point]
    source_label_position: T.Optional[Point]
    target_label_position: T.Optional[Point]

    def render(self, renderer):
        if self.line.label_box:
            assert self.label_box_layout
            self.label_box_layout.render(renderer)
            renderer.draw_line(
                self.source_to_aux_points,
                source_marker=self.line.source_marker,
                line_style=self.line.line_style) # TODO: clean
            renderer.draw_line(
                self.aux_to_target_points,
                target_marker=self.line.target_marker,
                line_style=self.line.line_style) # TODO: clean
        else:
            renderer.draw_line(
                self.source_to_aux_points + self.aux_to_target_points, # TODO: clean
                source_marker=self.line.source_marker,
                target_marker=self.line.target_marker,
                line_style=self.line.line_style)
            
        if self.line.source_label:
            assert self.source_label_position
            renderer.draw_texts(
                position=self.source_label_position,
                width=None,
                alignment='left',
                texts=[Text(text=self.line.source_label, font='normal', font_size='normal')])
            
        if self.line.target_label:
            assert self.target_label_position
            renderer.draw_texts(
                position=self.target_label_position,
                width=None,
                alignment='left',
                texts=[Text(text=self.line.target_label, font='normal', font_size='normal')])



class DiagramSpecification:

    def __init__(self) -> None:
        self.item_by_id: dict[str, DiagramItem] = {}
        self.id_by_item: dict[DiagramItem, str] = {}
        self.top_connectors_by_item: dict[DiagramItem, int] = {}
        self.bottom_connectors_by_item: dict[DiagramItem, int] = {}

    def add(self, item: DiagramItem) -> None:
        assert item not in self.id_by_item
        id_ = f'i{len(self.id_by_item)}'
        self.item_by_id[id_] = item
        self.id_by_item[item] = id_
        item.on_add(self)
        
    def iter_texts(self):
        return itertools.chain.from_iterable(item.iter_texts() for item in self.id_by_item)

    def get_hash(self) -> str:
        hash_obj = hashlib.sha256()
        hash_obj.update(repr(self.item_by_id).encode('utf-8'))
        return hash_obj.hexdigest()

    def make_layout(self, renderer: Renderer) -> DiagramLayout:
        children: list[dict] = []
        edges: list[dict] = []
        id_mapping_by_item_id: dict[str, dict[str, str]] = {}
        for item_id, item in self.item_by_id.items():
            item_id_mapping, item_children, item_edges = item.elk_source(item_id, self, renderer)
            id_mapping_by_item_id[item_id] = item_id_mapping
            children.extend(item_children)
            edges.extend(item_edges)

        elk_input = {
            'id': 'root',
            'layoutOptions': {
                'algorithm': 'layered',
                'elk.direction': 'DOWN'},
            'children': children,
            'edges': edges}

        with (ELK_JS_DIR / 'elk_source.json').open('w', encoding='utf-8') as elk_source_file:
            json.dump(elk_input, elk_source_file, indent=2)
            
        check_dependencies()

        cmd = [NODE_PATH, ELK_JS_DIR / 'run_elk.js']
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as elk_process:
            elk_stdout, elk_stderr = elk_process.communicate()
        assert not elk_stderr, elk_stderr
        elk_output = json.loads(elk_stdout)

        data_by_id = {}
        for section in ('children', 'edges'):
            for data in elk_output.get(section, ()):
                data_id = data.get('id')
                assert data_id
                assert data_id not in data_by_id
                data_by_id[data_id] = data

        layouts: list[ItemLayout] = []

        for item_id, item in self.item_by_id.items():
            item_id_mapping = id_mapping_by_item_id[item_id]
            layout_kwargs = {}
            for data_id, data_name in item_id_mapping.items():
                data = data_by_id.pop(data_id, None)
                assert data
                assert data_name not in layout_kwargs
                layout_kwargs[data_name] = data
            layouts.append(item.layout(**layout_kwargs))

        return DiagramLayout(
            self,
            origo=Point(float(elk_output['x']), float(elk_output['y'])),
            width=float(elk_output['width']),
            height=float(elk_output['height']),
            layouts=layouts)

@define
class DiagramLayout:
    specification: DiagramSpecification
    origo: Point
    width: float
    height: float
    layouts: list[ItemLayout]

    def render(self, renderer: Renderer):
        for layout in self.layouts:
            layout.render(renderer)


class Renderer:

    @classmethod
    def get_result(cls,
            specification: DiagramSpecification,
            out: T.Optional[pathlib.Path]=None,
            cache_dir: T.Optional[pathlib.Path]=None):

        result = None

        if cache_dir:
            specification_hash = specification.get_hash()
            cached_diagram_path = cache_dir / f'{specification_hash}.{cls.extension}'
            if cached_diagram_path.is_file():
                result = cls.read_result(cached_diagram_path)

        if result is None:
            result = cls(specification).result
            if cache_dir:
                cls.write_result(cached_diagram_path, result)
        
        if out:
            cls.write_result(out, result)

        return result

    @classmethod
    def write_result(self, path: pathlib.Path, result: object):
        raise NotImplementedError()

    def __init__(self, specification):
        self._register_texts(specification)
        layout = specification.make_layout(self)
        self._init_layout(layout)
        layout.render(self)

    @property
    def result(self):
        raise NotImplementedError()

    def _register_texts(self, specification: DiagramSpecification):
        pass

    def _init_layout(self, layout: DiagramLayout):
        pass



class SvgRenderer(Renderer):

    extension = 'svg'
    marker_size = 10
    marker_defs=f'''
      <defs xmlns="{SVG}">
        <marker
            id="uml-marker-closed_arrow"
            viewBox="-2 -2 {marker_size+4} {marker_size+4}"
            refX="{marker_size}"
            refY="{0.5*marker_size}"
            markerWidth="{marker_size+4}"
            markerHeight="{marker_size+4}"
            orient="auto-start-reverse">
          <path
              d="M 0 0 L {marker_size} {0.5*marker_size} L 0 {marker_size} Z"
              stroke-linejoin="round"
              stroke-linecap="round"
              class="uml-foreground-stroke uml-background_color-background"
          />
        </marker>
        <marker
            id="uml-marker-open_arrow"
            viewBox="-2 -2 {marker_size+4} {marker_size+4}"
            refX="{marker_size}"
            refY="{0.5*marker_size}"
            markerWidth="{marker_size+4}"
            markerHeight="{marker_size+4}"
            orient="auto-start-reverse">
          <path
              d="M 0 0 L {marker_size} {0.5*marker_size} L 0 {marker_size}"
              stroke-linejoin="round"
              stroke-linecap="round"
              fill="none"
              class="uml-foreground-stroke"
          />
        </marker>
        <marker
            id="uml-marker-filled_diamond"
            viewBox="-2 -2 {marker_size+4} {marker_size+4}"
            refX="{marker_size}"
            refY="{0.5*marker_size}"
            markerWidth="{marker_size+4}"
            markerHeight="{marker_size+4}"
            orient="auto-start-reverse">
          <path
              d="M 0 {0.5*marker_size} L      {0.5*marker_size} {0.2*marker_size}        {marker_size} {0.5*marker_size}      {0.5*marker_size} {0.8*marker_size} Z       "
              stroke-linejoin="round"
              stroke-linecap="round"
              class="uml-foreground-stroke uml-background_color-foreground"
          />
        </marker>
      </defs>'''

    @classmethod
    def write_result(cls, path: pathlib.Path, result):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(etree.tostring(result, encoding='utf-8'))

    @classmethod
    def read_result(cls, path):
        return etree.parse(path).getroot()

    @property
    def result(self):
        return self.svg

    def _init_layout(self, layout: DiagramLayout):

        self.svg = etree.Element(SVG.svg)

        x0 = layout.origo.x
        y0 = layout.origo.y
        self.svg.attrib['width'] = f'{layout.width}px'
        self.svg.attrib['height'] = f'{layout.height}px'
        self.svg.attrib['viewBox'] = f'{x0} {y0} {x0+layout.width} {y0+layout.height}'

        # TODO: calculate style
        etree.SubElement(self.svg, SVG.style).text='''
            .uml-foreground-stroke {
                stroke: black;
                stroke-width: 1px;
            }
            
            .uml-foreground-fill {
                fill: black;
            }
            
            .uml-background_color-type {
                fill: #ffffcc;
            }
            
            .uml-background_color-main_type {
                fill: #ffff66;
            }
            
            .uml-background_color-instance {
                fill: blue;
            }
            
            .uml-background_color-background {
                fill: white;
            }
            
            .uml-background_color-foreground {
                fill: black;
            }
            
            .uml-font-normal {
                font-family: Arial;
            }
            
            .uml-font-element {
                font-family: Arial;
            }
            
            .uml-fontsize-normal {
                font-size: 10px;
            }

            .uml-fontsize-large {
                font-size: 12px;
            }
            
            .uml-source_marker-closed_arrow {
                marker-start: url(#uml-marker-closed_arrow);
            }
            
            .uml-source_marker-open_arrow {
                marker-start: url(#uml-marker-open_arrow);
            }
            
            .uml-source_marker-filled_diamond {
                marker-start: url(#uml-marker-filled_diamond);
            }

            .uml-target_marker-closed_arrow {
                marker-end: url(#uml-marker-closed_arrow);
            }
            
            .uml-target_marker-open_arrow {
                marker-end: url(#uml-marker-open_arrow);
            }
            
            .uml-target_marker-filled_diamond {
                marker-end: url(#uml-marker-filled_diamond);
            }

            '''

        self.svg.append(etree.XML(self.marker_defs))

    def get_text_size(self, text: Text):
        


        if 1:
            
            #text.font = 'element'
            #text.bold = False
           # text.italic = False
            text.font_size = 'large'
            

        
        
        scale = {
            'normal': 10.,
            'large': 12.}[text.font_size] # check with css
            
            
            
            
        if 1:
            width = sum(
                WIDTH_BY_CHAR[char] for char in text.text)
            
            if text.bold:
                width *= 1.1
            if text.italic:
                width *= 1.1
            
            return width*(scale/12), scale*1.15

        return scale * 0.52 * len(text.text), scale*1.15

    def draw_box(self, position: Point, width: float, height: float, frame: bool, background_color: BackgroundColor):
        etree.SubElement(self.svg, SVG.rect, {
            'class': ' '.join([
                'uml-background_color-' + background_color,
                'uml-foreground-stroke' if frame else '']),
            'x': str(position.x),
            'y': str(position.y),
            'width': str(width),
            'height': str(height)})

    def draw_line(self, points: list[Point], source_marker=None, target_marker=None, line_style: LineStyle='solid'):
        classes = ['uml-foreground-stroke']
        if source_marker:
            classes.append(f'uml-source_marker-{source_marker}')
        if target_marker:
            classes.append(f'uml-target_marker-{target_marker}')
        polyline_element = etree.SubElement(self.svg, SVG.polyline, {
            'class': ' '.join(classes),
            'points': ' '.join(f'{pt.x},{pt.y}' for pt in points),
            'fill': 'none'})
        
        if line_style == 'short_dash':
            polyline_element.attrib['stroke-dasharray'] = '4 2'

        else:
            assert line_style == 'solid'
        

    def draw_texts(self, position: Point, width: double, alignment: alignment, texts: list[Text]):
        
        if not texts:
            return
        
        text_element = etree.SubElement(self.svg, SVG.text)

        height = 0
        
        for text in texts:
            if text.link:
                tspan_parent_element = etree.SubElement(text_element, SVG.a, {'href': text.link})
            else:
                tspan_parent_element = text_element
                
            if text.font_size == 'normal':
                height = max(height, 10.)
            else:
                height = max(height, 12.)

            tspan_attrib = {
                'class': ' '.join([
                    'uml-foreground-fill',
                    f'uml-font-{text.font}',
                    f'uml-fontsize-{text.font_size}',
                    ])}

            if text.bold:
                tspan_attrib['font-weight'] = 'bold'
            if text.italic:
                tspan_attrib['font-style'] = 'italic'
            if text.underlined:
                tspan_attrib['text-decoration'] = 'underline'

            tspan_element = etree.SubElement(tspan_parent_element, SVG.tspan, tspan_attrib)
            tspan_element.text = text.text.replace(' ', NBSP)

        if alignment == 'left':
            text_element.attrib['x'] = str(position.x)
        else:
            assert alignment == 'center'
            text_element.attrib['x'] = str(position.x + 0.5*width)
            text_element.attrib['text-anchor'] = 'middle'
            
        # Make layout agnostic to any whitespace between <tspan> elements, e.g., to line breaks
        # from prettyprint.
        text_element.attrib['font-size'] = '0px'
            
        BASELINE_FACTOR = 0.87 # TODO: calculate???    
        
        text_element.attrib['y'] = str(position.y + BASELINE_FACTOR * height)
        
        if False:
        
        
            etree.SubElement(self.svg, SVG.rect,
             {
                 'x': str(position.x - 10),
                 'y': str(position.y),
                 'width': '5',
                 'height': str(height),
                 'stroke': 'black',
                 'fill': 'green',
                 
                 
                 })


class LaTeXRenderer(Renderer):
    
    extension = 'tex'
    
    global_scale = 1
    
    _width_by_tex_text: dict[str, float] = {}
    
    @classmethod
    def write_result(cls, path: pathlib.Path, result):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(result, encoding='utf-8') # TODO: encoding?

    @classmethod
    def read_result(cls, path):
        return path.read_text(encoding='utf-8') # TODO: encoding?
    
    
    
    @property
    def result(self):
        if self.code is None:
            self.code_parts.append(r'\end{tikzpicture}')
            self.code = '\n'.join(self.code_parts)
        return self.code
    
    
    def _register_texts(self, specification: DiagramSpecification):
        
        to_calculate: set[str] = set()
        for text in specification.iter_texts():
            tex_text = self.text_to_tex(text)
            if tex_text not in self._width_by_tex_text:
                to_calculate.add(tex_text)
                
        if to_calculate:
            self._width_by_tex_text.update(self._calculate_text_widths(to_calculate))
            
            
    _text_calculation_start = r'''
        \def\sphinxdocclass{book}
        \documentclass[10pt,english]{scrbook}
        \usepackage{printlen}
        \usepackage{hyperref}
        \usepackage{tikz}
        
        % This provides a bold+italic style for sf!
        \usepackage{lmodern}
        
        
        
        \usetikzlibrary{patterns} 
        \begin{document}
        \newlength{\gnat}'''
    
    _text_calculation_end = r'''
        \end{document}'''
    
    
            
                
    def _calculate_text_widths(self, tex_texts: set[str]):
        
        latex_code_parts = [
            self._text_calculation_start]
        
        for nr, text in enumerate(tex_texts):
            latex_code_parts += [
                fr'\settowidth{{\gnat}}{{{text}}}',
                fr'\message{{--WIDTH--\printlength{{\gnat}}--}}']
                
        latex_code_parts.append(self._text_calculation_end)
        latex_code = '\n'.join(latex_code_parts)
        
        
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir = pathlib.Path(tmp_dir_name)
            tex_path = tmp_dir / 'calculate_widths.tex'
            tex_path.write_text(latex_code, encoding='utf-8')
            # print("CALL", tex_path.name)
            tex_result = subprocess.check_output(
                ['pdflatex', tex_path.name],
                cwd=tmp_dir)

        width_matches = list(re.finditer(
            rb'--WIDTH--\\def pt\{pt\}(?P<width>[0-9]*\.?[0-9]*)pt--',
            tex_result))
        
        assert len(width_matches) == len(tex_texts)
        
        result: dict[str, float] = {}
        
        for tex_text, width_match in zip(tex_texts, width_matches):
            width_string = width_match['width']
            width = float(width_string)
            result[tex_text] = width
        
        return result
                
                
                

    
    
    def _init_layout(self, layout: DiagramLayout):
        
       # for text in layout.
        
        
        
        
        
        
        
        
        self.scale = 0.02
        
        self.height = layout.height
        
        
        self.code = None
        
        self.code_parts: list[str] = [
            r'\begin{tikzpicture}']
        
        return
        

    
    
    def get_text_size(self, text: Text):
        

        
        width = self._width_by_tex_text[self.text_to_tex(text)]
        
  
            
            
        


            
            

        
        
        scale = {
            'normal': 10.,
            'large': 12.}[text.font_size] # check with css
            
            
            
            
        if 1:
           # width = sum(
           #     WIDTH_BY_CHAR[char] for char in text.text)
            
           # if text.bold:
           #     width *= 1.1
           # if text.italic:
           #     width *= 1.1
            
            return 1.88*width/self.global_scale, scale*1.55/self.global_scale

        return scale * 0.52 * len(text.text), scale*1.15
    
    
    def draw_box(self, position: Point, width: float, height: float, frame: bool, background_color: BackgroundColor):
        
        opp_position = position + Point(width, height)
        fill = {
            'type': 'lime',
            'main_type': 'yellow',
            'background': 'white'}[background_color]
        command = r'\draw' if frame else r'\fill'
        self.code_parts.append(fr'{command}[fill={fill}] {self.point_to_tex(position)} rectangle {self.point_to_tex(opp_position)};')

        
    def point_to_tex(self, point):
        return f'({self.global_scale*self.scale*point.x},{self.global_scale*self.scale*(self.height-point.y)})'
    
    def length_to_tex(self, length):
        print('++++++++++++++++', length, self.global_scale*self.scale*length)
        return self.scale*length

    def draw_line(self, points: list[Point], source_marker=None, target_marker=None, line_style: LineStyle='solid'):

        line_parts = [r'\draw']
        
        if source_marker or target_marker:
            markercode = '['
            if source_marker:
                markercode += {
                    'filled_diamond': '{Diamond}',
                    'closed_arrow': '{Triangle[open]}'}[source_marker]
            markercode += '-'
            if target_marker:
                markercode += {'open_arrow': '{Stealth}'}[target_marker]
            markercode += ']'
            line_parts.append(markercode)

        if line_style == 'short_dash':
            line_parts.append('[dashed]')

        line_parts.append(self.point_to_tex(points[0]))
        for point in points[1:]:
            line_parts.append(f'--{self.point_to_tex(point)}')
        line_parts.append(';')
        line = ''.join(line_parts)
        self.code_parts.append(line)
        
 
            
    font_to_tex = {
        'normal': r'\textsf',#r'\textsf',
        'element': r'\textsf',#r'\textsf'}
        }
    
    font_size_to_tex = {
        'normal': r'\footnotesize', #r'\normalsize',
        'large': r'\small', #r'\large',
        }
    
    bold_to_tex = {
        True: r'\textbf',
        False: ''
        }
    
    italic_to_tex = {
        True: r'\emph',
        False: ''
    }
    
    
            
    def text_to_tex(self, text):
            # text: str
            # font: Font
            # font_size: FontSize
            # link: T.Optional[str]=None
            # bold: bool=False
            # italic: bool=False
            # underlined: bool=False
            
            
            
        # strut
        


        
        tex_parts = [
            '{',
            self.font_to_tex[text.font],
                        '{',
            self.font_size_to_tex[text.font_size],
                      '{',
            self.italic_to_tex[text.italic],
             '{',
            
            self.bold_to_tex[text.bold],

           '{',
            self.tex_escape(text.text),
            '}}}}}']
        
        return ''.join(tex_parts)
    
    
    
    
    tex_escape_map = {
        '|': r'$\vert$',
        '<': r'$<$',
        '>': r'$>$'}

    
    def tex_escape(self, text: str) -> str:
        return ''.join(self.tex_escape_map.get(char, char) for char in text)


    def draw_texts(self, position: Point, width: double, alignment: Alignment, texts: list[Text]):
        
        font_sizes = set(text.font_size for text in texts)
        font_sizes = set({'large': 12, 'normal': 10}[font_size] for font_size in font_sizes)
        font_size = max(font_sizes)
        tex_text = ''.join(self.text_to_tex(text) for text in texts)
    
        position += Point(0, 0.85*font_size)
        if alignment == 'left':
            anchor = '[anchor=west]'
        else:
            anchor = ''
            position += Point(0.5*width, 0)
            
        self.code_parts.append(
            fr'\node{anchor} at {self.point_to_tex(position)} {{\strut{tex_text}}};')


class DiagramSpecificationBuilder:

    def __init__(self, *, get_link: T.Optional[LinkGetter]=None):
        self.diagram_specification = DiagramSpecification()
        self.get_link = get_link or (lambda element: None)
        self.node_by_element: dict[metamodel.Element, Node] = {}


    def get_node_id(self, element: T.Optional[metamodel.Element]) -> str:
        node = self.node_by_element.get(element)
        if not node:
            print(element)
            TODO
        id_ = self.diagram_specification.id_by_item.get(node)
        if not id_:
            TODO
        return id_


    def add_type_expression_box(
            self, type_expr: metamodel.TypeExpression, is_main_element: bool) -> None:
        header_rows = []
        if isinstance(type_expr, metamodel.Enumeration):
            header_rows.append(self.stereotype_row('enumeration'))
        elif isinstance(type_expr, metamodel.PrimitiveType):
            header_rows.append(self.stereotype_row('primitive'))
        elif isinstance(type_expr, metamodel.DataType):
            header_rows.append(self.stereotype_row('datatype'))
        elif isinstance(type_expr, metamodel.UnionType):
            header_rows.append(self.stereotype_row('union'))
        elif isinstance(type_expr, metamodel.BoundType):
            header_rows.append(self.stereotype_row('bind'))

        if isinstance(type_expr, metamodel.Type):
            header_rows.append(self.title_row(
                type_expr.name,
                font='element',
                bold=True,
                italic=type_expr.isAbstract,
                link=self.get_link(type_expr)))
        sections: list[Section] = [Table(rows=header_rows)]

        top_right_table = None
        if isinstance(type_expr, (metamodel.Class, metamodel.AggregatedDataType)):
            template_parameter_rows = []
            for template_parameter in type_expr.ownedParameters:
                cell_1 = Cell(
                    alignment='left',
                    parts=[
                        Text(
                            text=template_parameter.name,
                            font='element',
                            font_size='normal',
                            link=self.get_link(template_parameter)),
                        Text(
                            text=' :',
                            font='element',
                            font_size='normal')])
                cell_2 = Cell(
                    alignment='left',
                    parts=self.get_type_reference_texts(template_parameter.type, font_size='normal'))
                template_parameter_rows.append(Row([cell_1, cell_2]))
            if template_parameter_rows:
                top_right_table = Table(template_parameter_rows)

        if is_main_element and isinstance(type_expr, metamodel.Type):
            # Add Table with data properties to sections.
            property_rows = []
            for prop in type_expr.ownedAttributes:
                if not isinstance(prop, metamodel.DataProperty):
                    continue
                assert prop.name
                cell_1 = Cell(
                    alignment='left',
                    parts=[
                        Text(
                            text=prop.name,
                            font='element',
                            font_size='normal',
                            link=self.get_link(prop)),
                        Text(
                            text=' :',
                            font='element',
                            font_size='normal')])
                cell_2 = Cell(
                    alignment='left',
                    parts=self.get_type_reference_texts(prop.type, font_size='normal'))
                more_texts: list[str] = []
                multiplicity_string = multiplicity_label(prop.lower, prop.upper)
                if multiplicity_string:
                    more_texts.append(f'[{multiplicity_string}]')
                modifiers = []
                if prop.isOrdered:
                    modifiers.append('ordered')
                if prop.isUnique:
                    modifiers.append('unique')
                if modifiers:
                    more_texts.append(f'{{{", ".join(modifiers)}}}')
                if more_texts:
                    cell_2.parts.append(
                        Text(
                            text=' ' + ' '.join(more_texts),
                            font='element',
                            font_size='normal'))
                property_rows.append(Row([cell_1, cell_2]))
            if property_rows:
                sections.append(Separator())
                sections.append(Table(property_rows))
                
                
                
                
        if is_main_element and isinstance(type_expr, metamodel.Class):
            
          extensions =   type_expr._extensions
          
          for extension in extensions:

            # Add Table with data properties to sections.
            property_rows = []
            for prop in extension.ownedAttributes:
                if not isinstance(prop, metamodel.DataProperty):
                    continue
                assert prop.name
                cell_1 = Cell(
                    alignment='left',
                    parts=[
                        Text(
                            text=prop.name,
                            font='element',
                            font_size='normal',
                            link=self.get_link(prop)),
                        Text(
                            text=' :',
                            font='element',
                            font_size='normal')])
                cell_2 = Cell(
                    alignment='left',
                    parts=self.get_type_reference_texts(prop.type, font_size='normal'))
                more_texts: list[str] = []
                multiplicity_string = multiplicity_label(prop.lower, prop.upper)
                if multiplicity_string:
                    more_texts.append(f'[{multiplicity_string}]')
                modifiers = []
                if prop.isOrdered:
                    modifiers.append('ordered')
                if prop.isUnique:
                    modifiers.append('unique')
                if modifiers:
                    more_texts.append(f'{{{", ".join(modifiers)}}}')
                if more_texts:
                    cell_2.parts.append(
                        Text(
                            text=' ' + ' '.join(more_texts),
                            font='element',
                            font_size='normal'))
                property_rows.append(Row([cell_1, cell_2]))
            if property_rows:
                
                source_element = extension
                while source_element.owner:
                    source_element = source_element.owner
                
                sections.append(Separator())
                sections.append(Table([
                    Row([Cell(
                        alignment='left',
                        parts=[
                            Text(
                                text='from ',
                                font='element',
                                font_size='normal',
                                italic=True),
                            Text(
                                text=source_element.name+':',
                                font='element',
                                font_size='normal',
                                link=self.get_link(source_element),
                                italic=True)

                            
                            
                            
                            ])])]))
                
                sections.append(Table(property_rows))
                

                
                
        if is_main_element and isinstance(type_expr, metamodel.Enumeration):
            # Add Table with enumeration literals.
            literal_rows = []
            for literal in type_expr.ownedLiterals:
                literal_rows.append(self.texts_to_row(
                    alignment='left',
                    inlines=[Text(
                        text=literal.name,
                        font='normal',
                        font_size='normal',
                        link=self.get_link(literal))]))
            if literal_rows:
                sections.append(Separator())
                sections.append(Table(literal_rows))
                
        if isinstance(type_expr, metamodel.BoundType):
            bindung_rows = []
            for binding in type_expr.bindings:
                cell_1 = Cell(
                    alignment='left',
                    parts=[
                        Text(
                            text=binding.parameter.name,
                            font='element',
                            font_size='normal',
                            link=self.get_link(binding.parameter)),
                        Text(
                            text=' →',
                            font='element',
                            font_size='normal')])
                cell_2 = Cell(
                    alignment='left',
                    parts=self.get_type_reference_texts(binding.type, font_size='normal'))
                bindung_rows.append(Row([cell_1, cell_2]))
            if bindung_rows:
                sections.append(Separator())
                sections.append(Table(bindung_rows))

        box = Box(
            background_color='main_type' if is_main_element else 'type',
            frame=True,
            padding=5,
            sections=sections,
            top_right_table=top_right_table)
        self.node_by_element[type_expr] = box
        self.diagram_specification.add(box)


    def add_generalization_line(self, sub_type: metamodel.Type, super_type: metamodel.Type):
        line = Line(
            source_id=self.get_node_id(super_type),
            target_id=self.get_node_id(sub_type),
            source_marker='closed_arrow')
        self.diagram_specification.add(line)
        
        
    def add_binding_line(self, referrer: metamodel.TypeExpression, base: metamodel.TypeExpression):
        line = Line(
            source_id=self.get_node_id(referrer),
            target_id=self.get_node_id(base),
            target_marker='open_arrow',
            line_style='short_dash')
        self.diagram_specification.add(line)



    def add_object_property_line(self, prop: metamodel.ObjectProperty) -> None:
        
        label_rows = [self.texts_to_row(
            alignment='center',
            inlines=[Text(
                text=prop.name,
                font='element',
                link=self.get_link(prop),
                font_size='normal')])]

        label_box = Box(
            background_color='background',
            padding=2.,
            frame=False,
            sections=[Table(rows=label_rows)])

        line = Line(
            source_id=self.get_node_id(prop.owner),
            target_id=self.get_node_id(prop.type),
            label_box=label_box,
            source_label=multiplicity_label(prop.oppositeLower, prop.oppositeUpper) or None,
            source_marker='filled_diamond' if isinstance(prop, metamodel.CompositionProperty) else None,
            target_label=multiplicity_label(prop.lower, prop.upper) or None,
            target_marker='open_arrow')
        self.diagram_specification.add(line)


    def stereotype_row(self, stereotype: str) -> Row:
        text = Text(
            text=f'<<{stereotype}>>',
            font='normal',
            font_size='normal')
        return self.texts_to_row('center', [text])


    def title_row(self, title: str, *, font: Font, bold: bool=False, italic: bool=False, link: T.Optional[str]=None) -> Row:
        text = Text(
            text=title,
            font=font,
            link=link,
            font_size='large',
            bold=bold,
            italic=italic)
        return self.texts_to_row('center', [text])


    def texts_to_row(self, alignment: Alignment, inlines: list[Text]) -> Row:
        return Row([Cell(alignment, inlines)])
    
    def get_type_reference_texts(
            self, type_reference: metamodel.TypeExpression, font_size: FontSize):
        if isinstance(type_reference, (metamodel.Type, metamodel.TypeParameter)):
            return [Text(
                text=type_reference.name,
                font='element',
                font_size=font_size,
                link=self.get_link(type_reference))]
        elif isinstance(type_reference, metamodel.UnionType):
            texts = []
            for base_type in type_reference.bases:
                if texts:
                    texts.append(Text(
                        text=' | ',
                        font='element',
                        font_size=font_size))
                texts.extend(self.get_type_reference_texts(base_type, font_size=font_size))
            return texts

        elif isinstance(type_reference, metamodel.BoundType):
            texts = [
                Text(
                    text='<',
                    font='element',
                    font_size=font_size),
                Text(
                    text=type_reference.base.name,
                    font='element',
                    font_size=font_size,
                    link=self.get_link(type_reference.base)),
                Text(
                    text=' with ',
                    font='element',
                    font_size=font_size)]
            
            binding_texts: list[Text] = []
            for binding in type_reference.bindings:
                if binding_texts:
                    texts.append(
                        Text(
                            text=', ',
                            font='element',
                            font_size=font_size))
                texts += [
                    Text(
                        text=binding.parameter.name,
                        font='element',
                        font_size=font_size,
                        link=self.get_link(binding.parameter)),
                    Text(
                        text=' → ',
                        font='element',
                        font_size=font_size)]
                texts += self.get_type_reference_texts(binding.type, font_size=font_size)
            texts.extend(binding_texts)
            texts.append(
                Text(
                    text='>',
                    font='element',
                    font_size=font_size))

            return texts
            
        else:
            TODO
            
            
            



def make_diagram_specification(
        elements: T.Iterable[metamodel.Type], *,
        usages_by_class: dict[metamodel.Class, list[metamodel.ObjectProperty]],
        get_link: T.Optional[LinkGetter]=None):

    main_elements: set[metamodel.Type] = set()
    hierarchy_types: set[metamodel.Type] = set()

    for element in elements:
        if element in main_elements:
            continue
        main_elements.add(element)
        assert isinstance(element, metamodel.Type)
        hierarchy_types.add(element)
        hierarchy_types |= element.allSuperTypes

    type_expressions: set[metamodel.TypeExpression] = set(hierarchy_types)
    object_properties = set()

    sub_types_by_type: dict[metamodel.Type, set[metamodel.Type]] = {}

    for type_ in hierarchy_types:
        sub_types_by_type[type_] = set(type_.subTypes).intersection(hierarchy_types)

        for prop in type_.ownedAttributes:
            if isinstance(prop, metamodel.ObjectProperty):
                object_properties.add(prop)
                type_expressions.add(prop.type)
                
            for prop in sorted(
                    usages_by_class.get(type_, []),
                    key=lambda prop: prop.qualifiedName):
                
                if not isinstance(prop.type, metamodel.Class):
                    # Can we handle BoundClasses?
                    continue

                object_properties.add(prop)
                type_expressions.add(prop.owner)
        # TODO: opp props
      
      
        
    type_expressions_to_handle = type_expressions
    handled_type_expressions: set[metamodel.TypeExpression] = set()
    
    union_bases: list[tuple[metamodel.UnionType, metamodel.TypeExpression]] = []
    binding_bases: list[tuple[metamodel.BoundType, metamodel.Type]] = []
    
    while type_expressions_to_handle:
        type_expr = type_expressions_to_handle.pop()
        handled_type_expressions.add(type_expr)
        if isinstance(type_expr, metamodel.UnionType):
            for base in type_expr.bases:
                if base not in handled_type_expressions:
                    type_expressions_to_handle.add(base)
                union_bases.append((type_expr, base))
        elif isinstance(type_expr, metamodel.BoundType):
            if type_expr.base not in handled_type_expressions:
                type_expressions_to_handle.add(type_expr.base)
            binding_bases.append((type_expr, type_expr.base))
    type_expressions = handled_type_expressions
                    
        
        
    
    
    
    

    symbol_by_element = {}
    
    builder = DiagramSpecificationBuilder(get_link=get_link)

    for type_expr in sorted(type_expressions, key=repr):
        symbol_by_element[type_expr] = builder.add_type_expression_box(type_expr, type_expr in main_elements)
        

    for type_ in sorted(hierarchy_types, key=repr):
        for sub_type in sorted(sub_types_by_type[type_], key=lambda type_: type_.qualifiedName):
            builder.add_generalization_line(sub_type, type_)
    
    for prop in sorted(object_properties, key=lambda prop: prop.qualifiedName):
        builder.add_object_property_line(prop)
 
 
    for referrer, base in sorted(binding_bases, key=repr):
        builder.add_binding_line(referrer, base)
        
   # union_bases: list[tuple[metamodel.UnionType, metamodel.TypeExpression]] = []
   # binding_bases: list[tuple[metamodel.BoundType, metamodel.Type]] = []

    return builder.diagram_specification




GraphicsFormat = T.Literal['svg', 'tex']

def make_diagram(
        elements: T.Iterable[metamodel.Type], 
        format: GraphicsFormat, *,
        out: T.Optional[pathlib.Path]=None,
        get_link: T.Optional[LinkGetter]=None,
        cache_dir: T.Optional[pathlib.Path]=None,
        usages_by_class: T.Optional[dict[metamodel.Class, list[metamodel.ObjectProperty]]]):
    
    #if elements[0].name != 'Composition':
     ############################################################################################   return

    diagram_specification = make_diagram_specification(elements, get_link=get_link, usages_by_class=usages_by_class or {})
    renderer_cls = {
        'svg': SvgRenderer,
        'tex': LaTeXRenderer}[format]
        
    return renderer_cls.get_result(diagram_specification, out=out, cache_dir=cache_dir)


def sort_key(element: metamodel.Type):
    return element.qualifiedName



def multiplicity_label(lower: int, upper: T.Optional[int]):
    if upper is None:
        if lower == 0:
            return '*'
        else:
            return f'{lower}..*'
    elif lower == upper:
        if lower == 1:
            return ''
        else:
            return str(lower)
    else:
        return f'{lower}..{upper}'
    
    













WIDTH_BY_CHAR = { 
   "A": 8.00390625,
   "B": 8.00390625,
   "C": 8.666015625,
   "D": 8.666015625,
   "E": 8.00390625,
   "F": 7.330078125,
   "G": 9.333984375,
   "H": 8.666015625,
   "I": 3.333984375,
   "J": 6,
   "K": 8.00390625,
   "L": 6.673828125,
   "M": 9.99609375,
   "N": 8.666015625,
   "O": 9.333984375,
   "P": 8.00390625,
   "Q": 9.333984375,
   "R": 8.666015625,
   "S": 8.00390625,
   "T": 7.330078125,
   "U": 8.666015625,
   "V": 8.00390625,
   "W": 11.326171875,
   "X": 8.00390625,
   "Y": 8.00390625,
   "Z": 7.330078125,
   "a": 6.673828125,
   "b": 6.673828125,
   "c": 6,
   "d": 6.673828125,
   "e": 6.673828125,
   "f": 3.333984375,
   "g": 6.673828125,
   "h": 6.673828125,
   "i": 2.666015625,
   "j": 2.666015625,
   "k": 6,
   "l": 2.666015625,
   "m": 9.99609375,
   "n": 6.673828125,
   "o": 6.673828125,
   "p": 6.673828125,
   "q": 6.673828125,
   "r": 3.99609375,
   "s": 6,
   "t": 3.333984375,
   "u": 6.673828125,
   "v": 6,
   "w": 8.666015625,
   "x": 6,
   "y": 6,
   "z": 6,
   "0": 6.673828125,
   "1": 6.673828125,
   "2": 6.673828125,
   "3": 6.673828125,
   "4": 6.673828125,
   "5": 6.673828125,
   "6": 6.673828125,
   "7": 6.673828125,
   "8": 6.673828125,
   "9": 6.673828125,
   "_": 6.673828125,
   "<": 7.0078125,
   ">": 7.0078125,
   "[": 3.333984375,
   "]": 3.333984375,
   ".": 3.333984375,
   " ": 3.333984375,
   NBSP: 3.333984375,
   ' ': 3.333984375,
   ':': 2.5,
   '*': 6,
   '{': 4,
   '}': 4,
   ',': 3.5,
   '|': 2.5,
   '→': 11.,
   '\\': 0, # TODO
}
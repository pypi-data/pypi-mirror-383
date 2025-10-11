from __future__ import annotations


import contextlib
import datetime
import itertools
import os.path
from pathlib import Path
import shutil
import textwrap
import typing as T
from typing import TYPE_CHECKING

from docutils import nodes
from docutils.parsers.rst import directives
from lxml import etree
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain
from sphinx.util.docutils import SphinxDirective, ReferenceRole, SphinxRole
from pnb.mcl.metamodel import standard as metamodel
from pnb.mcl.io.xml import read_xmls, XmlExporter

from .toc_tree import find_model_names_in_toc_trees, SpeciPyTocTree
from dexpi.specificator.utils import uml_diagrams 

if TYPE_CHECKING:
    from pnb.mcl.metamodel import standard as metamodel
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.util.typing import ExtensionMetadata
    
THIS_DIR = Path(__file__).parent
    
NBSP = '\u00a0'
    
SP_CSS_PATH = THIS_DIR / 'sp.css'
    
# TODO move
def multiplicity_string(lower, upper):
    
    if upper is None:
        if lower == 0:
            return '*'
        else:
            return f'{lower}..*'
    elif lower == upper:
        return str(lower)
    else:
        return f'{lower}..{upper}'



def create_automodel_documents(app: Sphinx) -> None:
    specipy_domain = app.builder.env.domains.get('sp')
    assert isinstance(specipy_domain, SpeciPyDomain)
    specipy_domain.create_automodel_documents()
    

class ElementRole(ReferenceRole):
    
    def run(self):
        
        target = self.target
        title = self.title
        explicit_title = title is not target
        
        if target.startswith('~!'):
            target = '!~' + target[2:]
            
        if target.startswith('!'):
            target = target[1:]
            link = False
        else:
            link = True

        sp = self.env.get_domain('sp')
        
        if target.startswith('~'):
            if explicit_title: # TODO == vs is
                TODO
            element = sp.get_element(target[1:])
            if not element:
                # TODO error msg
                return [nodes.inline(classes=['sp-element sp-error'], text=target[1:])], []
            title = element.name
        else:
            element = sp.get_element(target)
            if not element:
                # TODO error msg
                return [nodes.inline(classes=['sp-element sp-error'], text=target)], []
                
        if link:
            return sp.get_element_reference(
                element, title, ref_docpath=self.inliner.document.current_source)
        else:
            return [nodes.inline(classes=['sp-element'], text=title)], []

        
class NameRole(SphinxRole):
    
    def run(self):
        return [nodes.inline(classes=['sp-element'], text=self.text)], []


        
class ColumnSpec:
    
    def __init__(self, header, fun):
        self.header = header
        self.fun = fun
    
    def entry(self, element, auto_dir, directive):
        content = self.fun(element, auto_dir, directive)
        
        if isinstance(content, addnodes.pending_xref):
            return nodes.entry('', nodes.paragraph('', '', content))
        if isinstance(content, str):
            return nodes.entry('', nodes.paragraph(text=content))
        if isinstance(content, nodes.inline):
            return nodes.entry('', nodes.paragraph('', '', content))
        if isinstance(content, nodes.reference):
            return nodes.entry('', nodes.paragraph('', '', content))
        if isinstance(content, nodes.image):
            return nodes.entry('', content)
        if isinstance(content, nodes.paragraph):
            return nodes.entry('', content)
        if isinstance(content, nodes.entry):
            return content
        if content is None:
            return None
        raise TypeError(content)
    
    def colspec(self):
        return nodes.colspec(colwidth=10)
    
        
    def header_entry(self):
        return nodes.entry('', nodes.paragraph(text=self.header))

    
    


        

class MemberListTable:
    
    def __init__(self, header, types, *column_specs):
        self.header = header
        self.types = types
        self.column_specs = column_specs
   
    def sections(self, auto_dir):
        if isinstance(auto_dir.element, metamodel.Namespace):
            members = auto_dir.element.members
        elif isinstance(auto_dir.element, metamodel.Object):
            members = []
            
            if auto_dir.element.type.name == 'SymbolCatalogue':
            
                for prop in auto_dir.element.type.attributes.values():
                    if isinstance(prop, metamodel.CompositionProperty):
                        for child in prop._get_values_(auto_dir.element):
                            if child.name:
                                members.append(child)
        else:
            raise TypeError(auto_dir.element)

        row_entries = []
        non_empty_col_numbers = set()
        for member in members:
            if isinstance(member, self.types):
                entries = [col.entry(member, auto_dir, auto_dir) for col in self.column_specs]
                all_entries_none = True
                for col_nr, entry in enumerate(entries):
                    if entry is not None:
                        non_empty_col_numbers.add(col_nr)
                        all_entries_none = False
                if not all_entries_none:
                    row_entries.append(entries)
                    
                

                
                
                
        #       rows.append(nodes.row('', *[col.entry(member, auto_dir, auto_dir) for col in self.column_specs]))
                
                
                
        #  nodes.entry('', nodes.paragraph(text=''))

        if row_entries:
            
            section = nodes.section(ids=[f'member-list-section-{self.header}'])
            section.append(nodes.title(text=self.header))
            yield section
            
            non_empty_col_numbers = sorted(non_empty_col_numbers)
            
            non_empty_cols = [self.column_specs[col_nr] for col_nr in non_empty_col_numbers]

            tgroup = nodes.tgroup()
            tgroup.extend(col.colspec() for col in non_empty_cols)
            thead = nodes.thead('', nodes.row('', *[col.header_entry() for col in non_empty_cols]))
            tgroup.append(thead)
            
            rows = []
            for entries in row_entries:
                entries_in_non_empty_cols = []
                for col_nr in non_empty_col_numbers:
                    entry = entries[col_nr]
                    if entry is None:
                        entry = nodes.entry('', nodes.paragraph(text=''))
                    entries_in_non_empty_cols.append(entry)
                rows.append(nodes.row('', *entries_in_non_empty_cols))
            tbody = nodes.tbody('', *rows)
            tgroup.append(tbody)
            table = nodes.table(align="left")
            table.append(tgroup)
            yield table            
            
            
            
            
            
            
            
            
            '''

            tgroup = nodes.tgroup()
            for col_nr in sorted(non_empty_col_numbers):
                tgroup.extend(self.column_specs[col_nr].colspec())
                
            thead = nodes.thead('', nodes.row('', *[col.header_entry() for col in self.column_specs]))
                
''
            
            
            thead = nodes.thead('', nodes.row('', *[col.header_entry() for col in self.column_specs]))
            tgroup.append(thead)
            tbody = nodes.tbody('', *rows)
            tgroup.append(tbody)
            table = nodes.table(align="left")
            table.append(tgroup)
            yield table'''

         
NAME_COLUMN = ColumnSpec(
    'Name',
    lambda element, auto_dir, directive: element.name)



def _name_column_with_ref_target(element, auto_dir, directive):
    
    labelid = directive.sp._get_element_ref_name(element)
    
    
    entry = nodes.entry()
    
    #, nodes.paragraph('', '', content))
    
    
    
    
    entry.append(nodes.target(refid=labelid))
    
    
    
   
    paragraph = nodes.paragraph(ids=[labelid], names=[labelid])
    
    paragraph.append(nodes.inline(text=element.name))
    entry.append(paragraph)
    
    
    ref_name = labelid.lower()
    
    
    standard_domain = directive.env.domains.standard_domain
    standard_domain.anonlabels[ref_name] = directive.env.docname, labelid
    standard_domain.labels[ref_name] = directive.env.docname, labelid, element.name


    
    
    
    
    
    
    
    
    
    return entry
    


NAME_COLUMN_WITH_REF_TARGET = ColumnSpec(
    'Name',
    _name_column_with_ref_target)

NAME_COLUMN_WITH_REF = ColumnSpec(
    'Name',
    lambda element, auto_dir, directive: auto_dir.get_element_reference(element))

MULTIPLICITY_COLUMN = ColumnSpec(
    'Multiplicity',
    lambda element, auto_dir, directive: multiplicity_string(element.lower, element.upper))


def type_expression_column_text(element, auto_dir, directive):
    paragraph = nodes.paragraph()
    paragraph.extend(format_type_expression(element.type, directive))
    return paragraph


    
def format_type_expression(type_expression, directive):
    parts = []
    if isinstance(type_expression, (metamodel.Type, metamodel.TypeParameter)):
        parts.append(directive.get_element_reference(type_expression))
    elif isinstance(type_expression, metamodel.UnionType):
        for base in type_expression.bases:
            if parts:
                parts.append(nodes.inline(text=' | '))
            parts.extend(format_type_expression(base, directive))
    elif isinstance(type_expression, metamodel.BoundType):
        parts += [
            nodes.inline(text='<'),
            directive.get_element_reference(type_expression.base)]
        binding_parts = []
        for binding in type_expression.bindings:
            if binding_parts:
                binding_parts.append(nodes.inline(text=', '))
            else:
                binding_parts.append(nodes.inline(text=' with '))
            binding_parts += [
                directive.get_element_reference(binding.parameter),
                nodes.inline(text=' → ')]
            binding_parts += format_type_expression(binding.type, directive)
        parts += binding_parts
        parts.append(nodes.inline(text='>'))
    else:
        raise TypeError(type_expression)
        TODO
    return parts






def symbol_preview_column(element, auto_dir, directive):
    if not isinstance(element, metamodel.Object):
        return

    if element.type.name != 'Symbol':
        return
    
    variant = element.Variants[0]
    assert variant.VariantNumber == 0

    from dexpilib.io.svg.writer import ShapeToSvg, Box
    
    color_cls = directive.sp.model_set['Core'].search_unique('Color', metamodel.Type)

    white = color_cls(R=255, G=255, B=255)
    box = Box(variant.MinX, variant.MaxX, variant.MinY, variant.MaxY)
    box.expand(1)
    svg = ShapeToSvg(directive.sp.model_set, variant, box, white)
    xml = svg.svg.xml()
    
    xml.attrib['width'] = f'{1*float(xml.attrib["width"])}mm'
    xml.attrib['height'] = f'{1*float(xml.attrib["height"])}mm'

    diagram_name = f'symbol-preview-{element.name}.svg'
    out_dir = directive.env.app.outdir / '_images'
    out_dir.mkdir(parents=True, exist_ok=True)
    etree.ElementTree(xml).write(out_dir / diagram_name)

    return nodes.image(uri=str(out_dir / diagram_name))


SYMBOL_PREVIEW_COLUMN = ColumnSpec(
    'Preview',
    symbol_preview_column)
    
    
def symbol_usage_column(element, auto_dir, directive):
    if not isinstance(element, metamodel.Object):
        return

    if element.type.name != 'Symbol':
        return

    usage = directive.sp.metadata.get(element, 'usage')

    if not usage:
        return None

    return directive.get_element_reference(directive.sp.get_element(usage))



def extended_type_column(element, auto_dir, directive):
    baseType = getattr(element, 'baseType', None)
    if not baseType:
        return
    return directive.get_element_reference(baseType)


EXTENDED_TYPE_COLUMN = ColumnSpec(
    'Extended Class',
    extended_type_column)

SYMBOL_USAGE_COLUMN = ColumnSpec(
    'Usage',
    symbol_usage_column)

TYPE_EXPRESSION_COLUMN = ColumnSpec(
    'Type',
    type_expression_column_text)

TEMPLATE_TYPE_EXPRESSION_COLUMN = ColumnSpec(
    'Default Type',
    type_expression_column_text)

TYPE_NAME_COLUMN = ColumnSpec(
    'Type',
    lambda element, auto_dir, directive: auto_dir.sp.get_type_name(element))

ORDERED_COLUMN = ColumnSpec(
    'Ordered',
    lambda element, auto_dir, directive: 'yes' if element.isOrdered else 'no')

def _rdl_uri_column(element, auto_dir, directive):
    rdl_uri = directive.sp.metadata.get(element, 'rdl_uri', None)
    if not rdl_uri:
        return None
    return nodes.reference(refuri=rdl_uri, text=rdl_uri)

RDL_URI_COLUMN = ColumnSpec(
    'RDL URI',
    _rdl_uri_column)

def _uom_symbol_column(element, auto_dir, directive):
    return directive.sp.metadata.get(element, 'un_symbol', None) # TODO rename uom!!!

UOM_SYMBOL_COLUMN = ColumnSpec(
    'Symbol',
    _uom_symbol_column)

UN_CODE_COLUMN = ColumnSpec(
    'UN Code',
    lambda element, auto_dir, directive: auto_dir.sp.metadata.get(element, 'un_code', None))

def _rdl_label_column(element, auto_dir, directive):
    return directive.sp.metadata.get(element, 'rdl_label', None)

RDL_LABEL_COLUMN = ColumnSpec(
    'RDL Label',
    _rdl_label_column)

UNIQUE_COLUMN = ColumnSpec(
    'Unique',
    lambda element, auto_dir, directive: 'yes' if element.isUnique else 'no')

OPPOSITE_MULTIPLICITY_COLUMN = ColumnSpec(
    'Opposite Multiplicity',
    lambda element, auto_dir, directive: multiplicity_string(element.oppositeLower, element.oppositeUpper))

PREVIEW_TEXT_COLUMN = ColumnSpec(
    '',
    lambda element, auto_dir, directive: auto_dir.get_preview_text(element))


def _preview_text_column_html_only(element, auto_dir, directive):
    if auto_dir.sp.is_html:
        return auto_dir.get_preview_text(element)

PREVIEW_TEXT_COLUMN_HTML_ONLY = ColumnSpec(
    '',
    _preview_text_column_html_only)


MEMBER_LIST_TABLES = [
    MemberListTable(
        'Packages',
        metamodel.Package,
        NAME_COLUMN_WITH_REF,
        PREVIEW_TEXT_COLUMN_HTML_ONLY),
    MemberListTable(
        'Classes',
        metamodel.Class,
        NAME_COLUMN_WITH_REF,
        TYPE_NAME_COLUMN,
        PREVIEW_TEXT_COLUMN_HTML_ONLY),
    MemberListTable(
        'Class Extensions',
        metamodel.ClassExtension,
        NAME_COLUMN_WITH_REF,
        EXTENDED_TYPE_COLUMN),
    MemberListTable(
        'Data Types',
        metamodel.DataType,
        NAME_COLUMN_WITH_REF,
        TYPE_NAME_COLUMN,
        PREVIEW_TEXT_COLUMN_HTML_ONLY),
    MemberListTable(
        'Literals',
        metamodel.EnumerationLiteral,
        NAME_COLUMN_WITH_REF_TARGET,
        UOM_SYMBOL_COLUMN,
        UN_CODE_COLUMN,
        RDL_LABEL_COLUMN,
        RDL_URI_COLUMN,
        PREVIEW_TEXT_COLUMN),
    MemberListTable(
        'Objects',
        metamodel.Object,
        NAME_COLUMN_WITH_REF,
        TYPE_EXPRESSION_COLUMN,
        SYMBOL_PREVIEW_COLUMN,
        SYMBOL_USAGE_COLUMN),
    MemberListTable(
        'Type Parameters',
        metamodel.TypeParameter,
        NAME_COLUMN_WITH_REF,
        TEMPLATE_TYPE_EXPRESSION_COLUMN,
        PREVIEW_TEXT_COLUMN_HTML_ONLY),
    MemberListTable(
        'Composition Properties',
        metamodel.CompositionProperty,
        NAME_COLUMN_WITH_REF,
        MULTIPLICITY_COLUMN,
        TYPE_EXPRESSION_COLUMN,
        ORDERED_COLUMN,
        PREVIEW_TEXT_COLUMN_HTML_ONLY),
    MemberListTable(
        'Reference Properties',
        metamodel.ReferenceProperty,
        NAME_COLUMN_WITH_REF,
        MULTIPLICITY_COLUMN,
        TYPE_EXPRESSION_COLUMN,
        ORDERED_COLUMN,
        UNIQUE_COLUMN,
        OPPOSITE_MULTIPLICITY_COLUMN,
        PREVIEW_TEXT_COLUMN_HTML_ONLY),
    MemberListTable(
        'Data Properties',
        metamodel.DataProperty,
        NAME_COLUMN_WITH_REF,
        MULTIPLICITY_COLUMN,
        TYPE_EXPRESSION_COLUMN,
        ORDERED_COLUMN,
        UNIQUE_COLUMN,
        PREVIEW_TEXT_COLUMN_HTML_ONLY),
    ]


class InternalAutoelementDirective(SphinxDirective):

    option_spec = {'element': directives.unchanged}
    
    diagram_nr = 0
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        sp = self.env.domains.get('sp')
        assert isinstance(sp, SpeciPyDomain)
        self.sp = sp
        self.element_qname: str = self.options.get('element')
        self.element = sp.get_element(self.element_qname)

    def run(self) -> int:
        
        if self.element_qname.endswith('.CustomAttribute') or self.element_qname.endswith('.CustomObject'):
            REMOVE
            return []

        return list(itertools.chain(
            self.hidden_toc(),
            self.navigation_bar(),
            self.overview(),
            self.member_lists(),
            self.details(),
            self.members_details(),
            self.example()))
        
        
    def navigation_bar(self):
        owners = [self.element]
        while owners[-1].owner:
            owners.append(owners[-1].owner)
        owners.reverse()
        owners_paragraph = nodes.paragraph()
        for owner in owners:
            if owner is not owners[0]:
                owners_paragraph.append(nodes.inline(text='::', classes=['sp-element']))
            if owner is self.element:
                owners_paragraph.append(nodes.inline(text=self.element.name, classes=['sp-element']))
            else:
                owners_paragraph.append(self.get_element_reference(owner))
        yield owners_paragraph
            

        
    def overview(self):
        
        description = self.sp.metadata.get(self.element, 'description', None)
        description_from_rdl = self.sp.metadata.get(self.element, 'description_from_rdl', None)
        if description_from_rdl:
            rdl_uri = self.sp.metadata.get(self.element, 'rdl_uri', None)
            assert rdl_uri
            description = description.strip()
            if description.endswith('.'):
                description = description[:-1]
                description = description + f' (from `{rdl_uri} <{rdl_uri}>`_).'

        return self.NEW_section(
            'Overview', [
                self.base_info(),
                self.rdl_paragraph_with_intro(self.element),
                self.nested_text(description),
                self.uml_diagram(),
                self.overview_tables()])


   
 
    def uml_diagram(self):
        
        
        if self.sp.is_html:
            return self.uml_diagram_html()
        else:
            assert self.sp.is_latex
            return self.uml_diagram_latex()
        
        
        
    def uml_diagram_html(self):
        

        if not isinstance(self.element, metamodel.Type):
            return []

 #       if self.element.name not in ['ConceptualModel', 'CentrifugalPump']:
 #           return []
        
        def get_link(element):
            
            if element is self.element:
                return None
            
            if target_doc_name := self.sp.doc_name_by_element.get(element):
                return f'../{target_doc_name}.html'
            else:
                # TODO: other cases?
                owner = element.owner
                target_doc_name = self.sp.doc_name_by_element.get(owner)
                return f'../{target_doc_name}.html#{self.sp._get_element_ref_name(element)}'

        diagram = uml_diagrams.make_diagram(
            [self.element],
            'svg',
            get_link=get_link,
            cache_dir=self.sp.cache_dir,
            usages_by_class=self.sp.usages_by_class)
        
        if diagram is None:
            return []

        InternalAutoelementDirective.diagram_nr += 1

        diagram_name = f'uml-{InternalAutoelementDirective.diagram_nr}.svg'

        out_dir = self.env.srcdir / 'auto_images'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / diagram_name
        assert not  out_path.is_file()
        etree.ElementTree(diagram).write(out_path)
        assert out_path.is_file()

        nesting_level = self.env.docname.count('/')
        refuri = nesting_level * '../' + '_images/' + diagram_name

        link_paragraph = nodes.paragraph()
        link_paragraph.extend([
            nodes.inline(text='('),
            nodes.reference(refuri=refuri, text='Fullscreen Diagram'),
            nodes.inline(text=')'),])

        return [
            link_paragraph,
            nodes.image(uri=f'/auto_images/{diagram_name}')]
        
        
    def uml_diagram_latex(self):


        if not isinstance(self.element, metamodel.Type):
            return []
        
        if self.element.name in [
                'NominalDiameterStandardClassification',
                'NominalPressureStandardClassification',
                'PureMaterialComponent']:
            return []

        diagram = uml_diagrams.make_diagram(
            [self.element],
            'tex',
            cache_dir=self.sp.cache_dir,
            usages_by_class=self.sp.usages_by_class)

        if diagram is None:
            return []

        InternalAutoelementDirective.diagram_nr += 1

        diagram_name = f'uml-{InternalAutoelementDirective.diagram_nr}.tex'

        out_dir = self.env.app.outdir
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / diagram_name
        assert not  out_path.is_file()
        
        # TODO: encoding?
        out_path.write_text(diagram, encoding='utf-8')
        
        return [nodes.image(uri=f'/{diagram_name}')]
                            


            
    def get_preview_text(self, element):
        
        description = self.sp.metadata.get(element, 'description', None)
        parsed_description = self.nested_text(description)
        if parsed_description and isinstance(parsed_description[0], nodes.paragraph):
            return parsed_description[0]
           
        
    def details(self):
        
        return self.nested_sections(self.sp.metadata.get(self.element, 'details', None))

                
        
    def rdl_data(self):
        REMOVE
        rdl_uri = self.sp.metadata.get(self.element, 'rdl_uri', None)
        rdl_label = self.sp.metadata.get(self.element, 'rdl_label', None)
        
        if not rdl_uri and not rdl_label:
            return []
        
        label = f'{rdl_label} ({rdl_uri})'
        paragraph = nodes.paragraph(text='RDL: ')
        paragraph.append(nodes.reference(refuri=rdl_uri, text=label))
        return [paragraph]
        
        
    def nested_text(self, text):
        # TODO: check no sections
        if not (text and text.strip()):
            return []
       
        with self.sp.nested_rst(self.env.docname):
            return self.parse_text_to_nodes(text, allow_section_headings=True)
            
        
    def nested_sections(self, text):
        # TODO: check no sections
        if not (text and text.strip()):
            return []
       
        with self.sp.nested_rst(self.env.docname):
            return self.parse_text_to_nodes(text, allow_section_headings=True)
        
        

        
        
        
    def hidden_toc(self):
        
        #if self.element.name == 'SymbolCatalogue':
        #    a=1
        
        children_with_doc = self.sp.get_element_children_with_own_doc(self.element)
        if children_with_doc:
            docnames = [self.sp.doc_name_by_element[child] for child in children_with_doc]
            toctree = addnodes.toctree()
            toctree['includefiles'] = docnames
            toctree['entries'] = [(None, docname) for docname in docnames]
            toctree['glob'] = None
            toctree['hidden'] = True
            yield toctree

    def base_info(self):
        
        if isinstance(self.element, metamodel.Object):
            node = nodes.rubric()
            node.extend([
                nodes.inline(text='Object ('),
                self.get_element_reference(self.element.type),
                nodes.inline(text=')'),])
            yield node
        elif isinstance(self.element, metamodel.ClassExtension):
            node = nodes.rubric()
            node.extend([
                nodes.inline(text='Class Extension of '),
                self.get_element_reference(self.element.baseType)])
            yield node
        else:
        
            yield nodes.rubric(text=self.sp.get_type_name(self.element))
        if isinstance(self.element, metamodel.Model):
            yield nodes.paragraph(text=f'URI: {self.element.uri}')
            
            code_paragraph = nodes.paragraph()
            code_paragraph.append(
                nodes.reference(refuri=f'../../_static/{self.element.name}.xml',
                                text=f'{self.element.name}.xml'))
            yield code_paragraph
 
                

    def section(self, header, content):
        if not isinstance(content, list):
            content = list(content)
        if content:
            section = nodes.section(ids=[header])
            section.append(nodes.title(text=header))
            section.extend(content)
            yield section
            
            
    def NEW_section(self, header, content):
        content = list(itertools.chain.from_iterable(content))
        if content:
            section = nodes.section(ids=[header])
            section.append(nodes.title(text=header))
            section.extend(content)
            yield section

            
    def overview_tables(self):
        
        if isinstance(self.element, metamodel.Type):
            if self.element.superTypes:
                yield nodes.rubric(text='Supertypes')
                list_ = nodes.bullet_list(bullet='-')
                for st in sorted(
                        self.element.superTypes,
                        key=lambda el: el.name):
                    para = nodes.paragraph()
                    para.append(self.get_element_reference(st))
                    li = nodes.list_item()
                    li.append(para)
                    list_.append(li)
                yield list_
                
            subTypes = self.element.subTypes
            if subTypes:
                yield nodes.rubric(text='Subtypes')
                list_ = nodes.bullet_list(bullet='-')
                for st in sorted(
                        subTypes,
                        key=lambda el: el.name):
                    
                    para = nodes.paragraph()
                    para.append(self.get_element_reference(st))
                    li = nodes.list_item()
                    li.append(para)
                    list_.append(li)
                yield list_
            
    def member_lists(self):

        yield from self.section(
            'Members',
            itertools.chain.from_iterable(table.sections(self) for table in MEMBER_LIST_TABLES))
   
    def get_element_reference(self, element, label=None):
        return self.sp.get_element_reference(element, label, ref_docname=self.env.docname)[0][0] # TODO
  
  
    def members_details(self):
        element = self.element
        if isinstance(element, metamodel.Type):
            for member in self.element:
                if isinstance(member, metamodel.Property):
                    yield from self.property_details(member)
                if isinstance(member, metamodel.TypeParameter):
                    yield from self.type_parameter_details(member)
        if isinstance(element, metamodel.ClassExtension):
            for member in self.element:
                if isinstance(member, metamodel.Property):
                    yield from self.property_details(member)
                    
                    
    def example(self):
        element = self.element
        if isinstance(element, metamodel.ConcreteClass):
            constructor = element
        else:
            constructor = None # TODO
            
        if constructor:
            
            constructor_kwargs = {}
            
            for prop in self.element.ownedAttributes:
                prop_example_value = self.sp.metadata.get(prop, 'exampleValue', None)
                if prop_example_value is None:
                    continue
                constructor_kwargs[prop.name] = prop_example_value

            example_value = constructor(**constructor_kwargs)
            
            
            model = metamodel.Model(name='example', uri='http://www.example.org')
            model.add(example_value)
            try:
                model_xml = XmlExporter(model).xml
            except Exception:
                model_xml = None
                
                
            if model_xml is not None:
                example_xml = None
                for child in model_xml:
                    if child.tag != 'Import':
                        if example_xml is not None:
                            RAISE
                        example_xml = child
                if example_xml is None:
                    RAISE
                xml_code = etree.tostring(example_xml, pretty_print=True).decode('utf-8')
                xml_code = textwrap.indent(xml_code, '   ')
                rst_code = f'.. code-block:: xml\n\n{xml_code}'
                section = nodes.section(ids=[f'{self.element.qualifiedName_chained}-example'])
                section.append(nodes.title(text='Example in DEXPI XML'))
                section.extend(self.parse_text_to_nodes(rst_code))
    
                yield section 
            
            
                    
                    
    def paragraph_with_intro(self, intro, content):
        paragraph = nodes.paragraph()
        paragraph.extend([
            nodes.strong(text=f'{intro}:'),
            nodes.inline(text=' ')])
        
        if isinstance(content, str):
            content = nodes.inline(text=content)
        if isinstance(content, nodes.Node):
            content = [content]
        paragraph.extend(content)
        return paragraph
    
    
    def rdl_paragraph_with_intro(self, element):

        
        rdl_uri = self.sp.metadata.get(element, 'rdl_uri', None)
        rdl_label = self.sp.metadata.get(element, 'rdl_label', None)
        if not rdl_uri and not rdl_label:
            return []
        if not (rdl_uri and rdl_label):
            RAISE
            
            
        if self.sp.is_html:
            label = f'{rdl_label} ({rdl_uri})'
            return [self.paragraph_with_intro('RDL', nodes.reference(refuri=rdl_uri, text=label))]
        else:
            return [
                self.paragraph_with_intro('RDL', nodes.reference(refuri=rdl_uri, text=rdl_uri)),
                nodes.paragraph(text=rdl_label)]
            
        


            
            
    def property_details(self, prop):
        section = self.sp.create_element_section(prop, self.env.docname)
        section.append(nodes.rubric(text=self.sp.get_type_name(prop)))
        section.extend(self.nested_text(self.sp.metadata.get(prop, 'description', None)))

        section.append(
            self.paragraph_with_intro(
                'Type',
                format_type_expression(prop.type, self)))
        section.append(
            self.paragraph_with_intro(
                'Multiplicity',
                multiplicity_string(prop.lower, prop.upper)))
        section.append(
            self.paragraph_with_intro(
                'Ordered',
                'yes' if prop.isOrdered else 'no'))
        if isinstance(prop, (metamodel.DataProperty, metamodel.ReferenceProperty)):
            section.append(
                self.paragraph_with_intro(
                    'Unique',
                    'yes' if prop.isUnique else 'no'))
        if isinstance(prop, metamodel.ReferenceProperty):
            section.append(
                self.paragraph_with_intro(
                    'Opposite Multiplicity',
                    multiplicity_string(prop.oppositeLower, prop.oppositeUpper)))
        section.extend(self.rdl_paragraph_with_intro(prop))

        section.extend(self.nested_sections(self.sp.metadata.get(prop, 'details', None)))
        
        
        example_value = self.sp.metadata.get(prop, 'exampleValue', None)
        if example_value is not None:
            example_section = nodes.section(ids=[f'{self.sp._get_element_ref_name(prop)}-example'])
            section.append(example_section)
            example_section.append(nodes.title(text='Example'))
            
            
            if isinstance(example_value, list):
                assert prop.lower <= len(example_value)
                assert prop.upper is None or prop.upper >= len(example_value)
                
                
                paragraph = nodes.paragraph(classes=['sp-dense'])
                paragraph.append(nodes.inline(text='['))
                example_section.append(paragraph)
                
                for nr, value in enumerate(example_value):
                    is_last_value = nr + 1 == len(example_value)
                    example_section.extend(self.value_representation_paragraphs(value, 1, True))
                    if not is_last_value:
                        example_section[-1].append(nodes.inline(text=','))
                        
                paragraph = nodes.paragraph(classes=['sp-dense'])
                paragraph.append(nodes.inline(text=']'))
                example_section.append(paragraph)
                

                

            else:
                assert prop.lower in [0, 1]
                assert prop.upper is None or prop.upper >= 1
            
                example_section.extend(self.value_representation_paragraphs(example_value))
        yield section

    def type_parameter_details(self, type_parameter):
        section = self.sp.create_element_section(type_parameter, self.env.docname)
        section.append(nodes.rubric(text=self.sp.get_type_name(type_parameter)))
        section.extend(self.nested_text(self.sp.metadata.get(type_parameter, 'description', None)))
        section.append(
            self.paragraph_with_intro(
                'Default Type',
                format_type_expression(type_parameter.type, self)))
        section.extend(self.nested_sections(self.sp.metadata.get(type_parameter, 'details', None)))
        yield section

        
    def member_groups(self, group_infos):
        for header, members, types, data in group_infos:
            members_in_group = [member for member in members if isinstance(member, types)]
            if members_in_group:
                yield header, members_in_group, data
                
                
                
    def value_representation_paragraphs(self, value, indent=0, indent_first=False):
        
        nbsp_per_indent = 5

        paragraphs = []
        
        def new_paragraph():
            paragraph = nodes.paragraph(classes=['sp-dense'])
            paragraph.append(nodes.inline(text=indent*nbsp_per_indent*NBSP))
            paragraphs.append(paragraph)
            return paragraph
        
        if indent_first:
            paragraph = new_paragraph()
        else:
            paragraph = nodes.paragraph(classes=['sp-dense'])
            paragraphs.append(paragraph)

        indent += 1

        if isinstance(value, str):
            paragraph.append(nodes.literal(text=f'"{value}"'))
        elif isinstance(value, bool):
            paragraph.append(nodes.literal(text=str(value).lower()))
        elif isinstance(value, int):
            paragraph.append(nodes.literal(text=str(value)))
        elif isinstance(value, float):
            paragraph.append(nodes.literal(text=str(value)))
        elif isinstance(value,datetime.datetime):
            paragraph.append(nodes.literal(text=value.isoformat()))
        elif isinstance(value, metamodel.EnumerationLiteral):
            paragraph.append(self.get_element_reference(value))
        elif isinstance(value, (metamodel.AggregatedDataValue, metamodel.Object)):
            paragraph.append(self.get_element_reference(value.type))
            paragraph.append(nodes.inline(text='('))
            for prop_nr, (prop, prop_values) in enumerate(
                    sorted(value._attribute_values_.items(),
                           key=lambda prop_and_values: prop_and_values[0].name)):
                is_last_prop = prop_nr + 1 == len(value._attribute_values_)

                paragraph = new_paragraph()
                paragraph.append(self.get_element_reference(prop))
                paragraph.append(nodes.inline(text=' = '))
                
                assert len(prop_values) >= prop.lower
                assert prop.upper is None or len(prop_values) <= prop.upper
                
                if prop.upper == 1:
                    prop_value_paragraphs = self.value_representation_paragraphs(prop_values[0], indent)
                    paragraph.extend(prop_value_paragraphs[0])
                    paragraphs.extend(prop_value_paragraphs[1:])
                    paragraph = paragraphs[-1]
                else:
                    paragraph.append(nodes.inline(text='['))
                    indent += 1
                    for nr, prop_value in enumerate(prop_values):
                        is_last_prop_value = nr + 1 == len(prop_values)
                        prop_value_paragraphs = self.value_representation_paragraphs(prop_value, indent, True)
                        paragraphs.extend(prop_value_paragraphs)
                        paragraph = paragraphs[-1]
                        if not is_last_prop_value:
                            paragraph.append(nodes.inline(text=','))
                    paragraph.append(nodes.inline(text=']'))
                    indent -= 1
                if not is_last_prop:
                    paragraph.append(nodes.inline(text=','))
            paragraph.append(nodes.inline(text=')'))
        else:
            paragraph.append(nodes.literal(text='mimi '+repr(value)))
        return paragraphs
            
        
        
                
                
            
            
        
        
        
    
            
            
        


class SpeciPyDomain(Domain):

    name = 'sp'
    label = 'SpeciPy'
    directives = {
        'internal-autoelement': InternalAutoelementDirective,
    }
    
    roles = {
        'element': ElementRole(),
        'name': NameRole(),
    }

    def __init__(self, env: BuildEnvironment) -> None:
        super().__init__(env)
        

        self._specificator_data: None | SpecificatorData = None

        self.doc_name_by_element: dict[metamodel.Model, str] = {}
        
        
        self._nested_docnames: list[str] = []
        
        self._usages_by_class = None
        self.usages_by_class

        
    @property
    def is_latex(self):
        return self.env.app.builder.name == 'latex'
    
    @property
    def is_html(self):
        return self.env.app.builder.name == 'html'
        
        

    @property
    def usages_by_class(self):
        usages_by_class = self._usages_by_class
        if usages_by_class is None:
            usages_by_class = {}
            
            namespaces_to_handle = set(self.model_set)
            handled_namespaces = set()
            while namespaces_to_handle:
                member = namespaces_to_handle.pop()
                
                if isinstance(member, metamodel.Namespace):
                    new_namespaces = set(member)
                    new_namespaces.difference_update(handled_namespaces)
                    namespaces_to_handle.update(new_namespaces)
                    
                if isinstance(member, metamodel.ObjectProperty):
                    prop_type = member.type

                    if isinstance(prop_type, metamodel.Class):
                        pass
                    elif isinstance(prop_type, metamodel.BoundClass):
                        prop_type = prop_type.base
                        assert isinstance(prop_type, metamodel.Class)
                    else:
                        raise Exception(type(prop_type))
                    usages_by_class.setdefault(prop_type, []).append(member)


            
            self._usages_by_class = usages_by_class
        return usages_by_class
            
            
        
        
    @contextlib.contextmanager
    def nested_rst(self, docname: str):
        self._nested_docnames.append(docname)
        yield
        self._nested_docnames.pop()
        
        
        
        
    @property
    def metadata(self) -> MetaData:
        assert len(self.model_set.metadata_by_name) == 1
        return list(self.model_set.metadata_by_name.items())[0][1]

    @property
    def cache_dir(self) -> Path | None:
        cache_dir = self._specificator_data.config.get('cache_dir')
        if cache_dir:
            return Path(str(cache_dir))
        else:
            return None

    @property
    def model_set(self) -> metamodel.ModelSet:
        return self.specificator_data.model_set

    @property
    def specificator_data(self) -> SpecificatorData:
        specificator_data = self._specificator_data
        if specificator_data is None:
            if not _DATA:
                raise Exception()
            specificator_data = self._specificator_data = _DATA
        return specificator_data
    
    #@property
    
    
    def get_element(self, qname: str):

        model_name, *sub_names = qname.split('.')
        element = self.model_set.get(model_name)
        if not element:
            return None
            TODO
        for name in sub_names:
            if type(element).__name__ == 'Object':
                child = None
                
                for prop in element.type.attributes.values():
                    if isinstance(prop, metamodel.CompositionProperty):
                        for child_ in prop._get_values_(element):
                            if child_.name == name:
                                child = child_
                                break
            else:
                try:
                    child = element.get(name)
                except Exception:
                    return None

            if not child:
                return None
                raise Exception(f'{element} has no member "{name}"')
                TODO
            element = child
        return element
    
    def create_automodel_documents(self):
        for doc_name in self.env.found_docs:
            doc_path = self.env.doc2path(doc_name)
            doc_raw = doc_path.read_text()
            for model_name in find_model_names_in_toc_trees(doc_raw):
                model = self.model_set.get(model_name)
                if not model:
                    continue
                    raise Exception(model_name)
                    TODO
                if model in self.doc_name_by_element:
                    TODO
                self._create_element_stub(model, doc_path.parent)
                
                
    def element_can_have_subdocs(self, element: metamodel.Element) -> bool:
        return isinstance(element, (metamodel.Model, metamodel.Package)) #, metamodel.Object))
                          
    def get_element_children_with_own_doc(self, element: metamodel.Element) -> list[metamodel.Element]:
        if isinstance(element, (metamodel.Model, metamodel.Package)):
            return [e for e in element.packagedElements if not isinstance(e, metamodel.Object)]
        return []
        
        if isinstance(element, (metamodel.Object)):
            
            children = []

            if element.type.name in ['SymbolCatalogue']:
                for prop in element.type.attributes.values():
                    if isinstance(prop, metamodel.CompositionProperty):
                        for child in prop._get_values_(element):
                            if child.name:
                                children.append(child)
            return children
                    

        return []
    
    
    def _get_element_ref_name(self, element):
        assert element not in self.doc_name_by_element
        # TODO: ambiguous refs due to 'lower'
        return f'sp:{element.qualifiedName}'.lower()
    
    
    def create_element_section(self, element, docname):
        
        labelid = self._get_element_ref_name(element)
        section = nodes.section(ids=[labelid])
        
        section.append(nodes.title(text=element.name))
        
        ref_name = self._get_element_ref_name(element).lower()

        standard_domain = self.env.domains.standard_domain
        standard_domain.anonlabels[ref_name] = docname, labelid
        standard_domain.labels[ref_name] = docname, labelid, element.name
        return section

        
          
    
    
    def get_element_reference(self, element, label=None, ref_docpath=None, ref_docname=None):
        
        if label is None:
            label = element.name
            
        nested_docname = self._nested_docnames[-1] if self._nested_docnames else None
        
        if nested_docname:
            assert ref_docname is None
            ref_docname = nested_docname
           # TODO: doc path for messages

        else:
            assert None in (ref_docpath, ref_docname)
            if ref_docname is None:
                assert ref_docpath
                ref_docname = self.env.path2doc(ref_docpath)

        if target_doc_name := self.doc_name_by_element.get(element):
            inline = nodes.inline(text=label)
            pending_xref = addnodes.pending_xref(
                classes=['sp-element'],
                refdoc=ref_docname,
                refdomain='std',
                refexplicit=True,
                reftarget=f'/{target_doc_name}',
                reftype='doc',
                refwarn=True)
            pending_xref.append(inline)
            return [pending_xref], []
        else:
            inline = nodes.inline(text=label)
            pending_xref = addnodes.pending_xref(
                classes=['sp-element'],
                refdoc=ref_docname,
                refdomain='std',
                refexplicit=True,
                reftarget=self._get_element_ref_name(element).lower(),
                reftype='ref',
                refwarn=True)
            pending_xref.append(inline)
            return [pending_xref], []

                
                
    


    def _create_element_stub(self, element, parent_dir):
        
        if type(element).__name__ == 'Object':
            return
        
        if self.element_can_have_subdocs(element):
            element_dir = parent_dir / element.name
            # TODO: check existing dir at least for top-level model
            element_dir.mkdir(parents=True, exist_ok=True)
            element_path = element_dir / f'{element.get_meta_class_name().lower()}-index.rst'
            for child in self.get_element_children_with_own_doc(element):
                self._create_element_stub(child, element_dir)
        else:
            
            if type(element).__name__ == 'Object':
                a=1
            
            element_path = parent_dir / f'{element.name}.rst'
        header = '\n'.join((
            element.name,
            len(element.name) * '=',
            '',
            '.. sp:internal-autoelement::',
            f'   :element: {element.qualifiedName_chained}'))
        element_path.write_text(header)
        self.doc_name_by_element[element] = self.env.path2doc(element_path)

    def get_type_name(self, type_or_element: metamodel.Element | T.Type[metamodel.Element]) -> str:
        if isinstance(type_or_element, metamodel.Element):
            type_ = type(type_or_element)
        else:
            type_ = type_or_element
        return dict(
            AggregatedDataType='Aggregated Data Type',
            Model='Model',
            Package='Package',
            AbstractClass='Abstract Class',
            ConcreteClass='Concrete Class',
            ClassExtension='Class Extension',
            DataProperty='Data Property',
            CompositionProperty='Composition Property',
            ReferenceProperty='Reference Property',
            DataTypeParameter='Data Type Parameter',
            ClassParameter='Class Parameter').get(type_.__name__, type_.__name__)
            
            
            
def on_build_finished(app, exception):
    shutil.copy(SP_CSS_PATH, app.outdir / '_static')
        
    

    


def setup(app: Sphinx) -> ExtensionMetadata:
    app.connect('builder-inited', create_automodel_documents)
    app.connect('build-finished', on_build_finished)
    app.add_directive('toctree', SpeciPyTocTree, override=True)
    app.add_domain(SpeciPyDomain)
    app.add_css_file('sp.css')

    # TODO: how to handle version; same as specificator?
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }


_MODEL_BY_NAME: None | dict[str, metamodel.Model] = None

from pnb.mcl.metamodel.standard import MetaData


_DATA = None

class SpecificatorData:
    
    def __init__(self, model_set, config):
        self.model_set = model_set
        self.config = config
        
    

_DATA: T.Optional[SpecificatorData] = None



@contextlib.contextmanager
def set_data(data: SpecificatorData):
    global _DATA
    if _DATA is not None:
        raise Exception('specificator data already set')
    _DATA = data
    
    yield
    
    _DATA = None
    
    

    
    
    






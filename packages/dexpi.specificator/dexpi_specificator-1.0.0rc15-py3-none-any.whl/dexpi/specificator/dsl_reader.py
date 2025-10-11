from __future__ import annotations

# pylint: disable=missing-docstring, too-few-public-methods

import atexit
import datetime
import inspect
import logging
import json
from pathlib import Path
import re
import textwrap
import traceback
import typing as T

import rdflib

from pnb.mcl.metamodel import standard as metamodel
from pnb.mcl.utils import IDENTIFIER_PATTERN

LOGGER = logging.getLogger(__name__)

DOCUMENTATION_URL = 'https://www.dexpi.org/TODO/'

_NOT_GIVEN = object()


class Source:
    pass


class PySource(Source):

    def __init__(self, path: Path, lineno: int) -> None:
        self.path = path
        self.lineno = lineno

    def __str__(self) -> str:
        
        return f'File "{self.path}", line {self.lineno}'


def py_source_from_calling_frame(extra_frames=0):
    # TODO: doc
    """
    Standard way:
    
        call_info = inspect.getframeinfo(frame)
        return PySource(Path(call_info.filename), call_info.lineno)
    """
    assert extra_frames >= 0
    frame = inspect.currentframe()
    # +1 for the frame calling this function (the frame w.r.t. which we want the calling frame)
    # +1 for the frame of this function
    for _ in range(extra_frames + 2):
        frame = frame.f_back
    filename = inspect.getsourcefile(frame) or inspect.getfile(frame)
    if inspect.istraceback(frame):
        lineno = frame.tb_lineno
    else:
        lineno = frame.f_lineno
    return PySource(Path(filename), lineno)





def context_sort_key(context: ElementInfo | ElementSpecification):
    if isinstance(context, ElementInfo):
        return (1, str(context._source_))
    else:
        assert isinstance(context, ElementSpecification)
        return (2, str(context.qname))



class Message:
    
    level: str
    id: str
    text: str

    def __init__(self, contexts: list[ElementInfo | ElementSpecification], causes: T.Optional[list[Message]]=None) -> None:
        
        self.nr: T.Optional[int] = None
        self.contexts = sorted(contexts, key=context_sort_key)
        if causes:
            causes = sorted(causes, key=lambda msg: msg.nr)
        else:
            causes = []
        self.causes = causes

    def __str__(self) -> str:

        result_rows = [
            f'#{self.nr} --- {self.level}: {self.id} ---']

        for context in self.contexts:
            if isinstance(context, ElementInfo):
                result_rows.append(f'- {context._source_}')
                if context_description := context._get_description_():
                    result_rows.append(f'  {context_description}')
            else:
                result_rows.append(f'- {context.qname}')
                for info in sorted(context.infos, key=context_sort_key):
                    result_rows.append(f'  - {info._source_}')
                    if info_description := info._get_description_():
                        result_rows.append(f'    {info_description}')

        if self.causes:
            causes_repr = ' '.join(f'#{cause.nr}' for cause in self.causes)
            result_rows.append(f'causes: {causes_repr}')

        result_rows += [
            self.text,
            f'(see {DOCUMENTATION_URL}{self.id})']

        return '\n'.join(result_rows)


class FatalErrorMessage(Message):

    level = 'FATAL ERROR'
    id = 'fatal-error'

    def __init__(self, base_traceback: str):
        super().__init__([])
        self.base_traceback = base_traceback

    @property
    def text(self):
        base_traceback_repr = textwrap.indent(self.base_traceback, '  ').rstrip()
        return (
            f'An error has occurred while reading the DSL source files:\n\n{base_traceback_repr}'
            f'\n\nThis error prevents any further processing of the source files.')
            
        
class ErrorMessage(Message):
    
    level = 'ERROR'


class MissingParameter(ErrorMessage):

    id = 'missing-parameter'
    
    def __init__(self, element_infos: list[ElementInfo], parameter_name: str) -> None:
        super().__init__(element_infos)
        self.parameter_name = parameter_name
        
    @property
    def text(self):
        return f'Parameter "{self.parameter_name}" is required, but missing.'
    
    
class InvalidParameterType(ErrorMessage):
    
    id = 'invalid-parameter-type'
    
    def __init__(self,
            element_infos: list[ElementInfo],
            parameter_name: str,
            value: T.Any,
            expected_types: tuple[type, ...]) -> None:
        super().__init__(element_infos)
        self.parameter_name = parameter_name
        self.value = value
        self.expected_types = expected_types
        
    
    @property
    def text(self):
        if len(self.expected_types) == 1:
            expected_types_repr = self.expected_types[0].__name__
        else:
            type_names = ', '.join(type_.__name__ for type_ in self.expected_types)
            expected_types_repr = f'one of {type_names}' 
        return (
            f'Parameter "{self.parameter_name}": got {self.value!r} of type '
            f'{type(self.value).__name__}, but value type must be {expected_types_repr}.')


class InvalidParameter(ErrorMessage):

    parameter_requirements: str

    def __init__(self,
            element_infos: list[ElementInfo],
            parameter_name: str,
            value: T.Any,
            causes: T.Optional[list[Message]]=None):
        super().__init__(element_infos, causes=causes)
        self.parameter_name = parameter_name
        self.value = value

    @property
    def text(self):
        return (
            f'Parameter "{self.parameter_name}": {self.value!r} is no valid value: '
            f'{self.parameter_requirements}')


class NoValidIdentifier(InvalidParameter):

    id = 'no-valid-identifier'
    parameter_requirements = (
        'An identifier must start with [a-zA_Z], followed by an arbitrary number of [a-zA_Z0-9_].')

    def __init__(self,
            element_infos: list[ElementInfo],
            parameter_name: str,
            value: str):
        super().__init__(element_infos, parameter_name, value)


class SkippedElementUsed(InvalidParameter):

    id = 'skipped-element-used'
    parameter_requirements = (
        'It has been skipped.')

    def __init__(self,
            element_infos: list[ElementInfo],
            parameter_name: str,
            value: str,
            causes: list[Message]):
        super().__init__(element_infos, parameter_name, value, causes=causes)


class NoOwner(ErrorMessage):

    id = 'no-owner'

    def __init__(self, element_info: ElementInfo):
        super().__init__([element_info])

    @property
    def text(self):
        return 'The element is skipped because it is not assigned to any owner.'


class OwnerSkipped(ErrorMessage):

    id = 'owner-skipped'

    def __init__(self, element_infos: list[ElementInfo], owner_element_infos: list[ElementInfo]):
        causes = set(info._error_ for info in owner_element_infos)
        causes.discard(None)
        assert causes
        super().__init__(element_infos, causes=list(causes))

    @property
    def text(self):
        return 'The element is skipped because its owner is skipped.'


class MissingMetatype(ErrorMessage):

    id = 'missing-metatype'

    def __init__(self, element_infos: list[ElementInfo]):
        super().__init__(element_infos)

    @property
    def text(self):
        return 'The element is skipped because no metatype is given.'


class MultipleMetatypes(ErrorMessage):

    id = 'multiple-metatypes'

    def __init__(self, element_infos: list[ElementInfo], metatypes: set[T.Type[metamodel.Element]]):
        super().__init__(element_infos)
        self.metatypes = metatypes

    @property
    def text(self):
        metatypes_repr = ', '.join(sorted(type_.__name__ for type_ in self.metatypes))
        return f'The element is skipped because multiple metatypes are given: {metatypes_repr}.'


class InvalidMemberType(ErrorMessage):

    id = 'invalid-member-type'

    def __init__(self,
            element_infos: list[ElementInfo],
            metatype: T.Type[metamodel.Element],
            owner_metatype: T.Type[metamodel.Element]):
        super().__init__(element_infos)
        self.metatype = metatype
        self.owner_metatype = owner_metatype

    @property
    def text(self):
        return (
            f'The element is skipped because its owner of type {self.owner_metatype.__name__} '
            f'cannot have a member of type {self.metatype.__name__}.')


class MultipleParameterValues(ErrorMessage):

    id = 'multiple-parameter-values'

    def __init__(self, element_infos: list[ElementInfo], parameter_name: str):
        super().__init__(element_infos)
        self.parameter_name = parameter_name

    @property
    def text(self):
        return (
            f'The value for parameter "{self.parameter_name}" is given several times. The '
            f'parameter is ignored.')


class CyclicDependency(ErrorMessage):

    id = 'cyclic-dependency'

    def __init__(self, specifications: list[ElementSpecification]):
        super().__init__(specifications)
        self.specifications = specifications

    @property
    def text(self):
        return 'Due to a cyclic dependency, these elements cannot be built.'


# TODO begin ok

class Reference:

    __slots__ = ('_source_', )

    _instances: T.Optional[list[Reference]] = None

    @staticmethod
    def track_instances():
        if Reference._instances is not None:
            raise RuntimeError('instances are already tracked')
        Reference._instances = []

    @staticmethod
    def get_instances() -> list[Reference]:
        if Reference._instances is None:
            raise RuntimeError('instances have not been tracked')
        instances = Reference._instances
        Reference._instances = None
        return instances

    def __init__(self, source: Source):
        if Reference._instances is not None:
            Reference._instances.append(self)
        self._source_ = source

    def __call__(self, **kwargs):
        return ReferenceCall(
            py_source_from_calling_frame(),
            owner=self,
            kwargs=kwargs)

    def __getitem__(self, key: object):
        return ReferenceItem(
            py_source_from_calling_frame(),
            owner=self,
            key=key)

    def __or__(self, other: Reference):
        return ReferenceConjunction(
            py_source_from_calling_frame(),
            first=self,
            second=other)
        
    def _resolve_(self):
        raise NotImplementedError(self)


class ReferenceConjunction(Reference):
    def __init__(self, source: Source, *, first: Reference, second: Reference):
        super().__init__(source)
        self.first = first
        self.second = second
    def _resolve_(self):
        first = self.first._resolve_()
        second = self.second._resolve_()
        for metatype in [metamodel.DataTypeExpression, metamodel.ClassExpression]:
            if isinstance(first, metatype) and isinstance(second, metatype):
                return metamodel.type_conjunction([first, second])
        RAISE


class ReferenceItem(Reference):
    def __init__(self, source: Source, *, owner: Reference, key: object):
        super().__init__(source)
        self.owner = owner
        self.key = key
        
    def _resolve_(self):
        
        binding_dict = self.key
        if not isinstance(binding_dict, dict):
            print(self._source_)
            ji
            raise Postpone() # TODO
        owner = self.owner._resolve_()
        if not isinstance(owner, (metamodel.Class, metamodel.AggregatedDataType)):
            print(vars(self))
            print(self._source_)
            print(vars(self._source_))
            RAISE
            
        if isinstance(owner, metamodel.Class):
            parameter_metatype = metamodel.TypeParameter
            bound_metatype = metamodel.BoundClass
        else:
            parameter_metatype = metamodel.DataTypeParameter
            bound_metatype = metamodel.BoundDataType
             
  
        bindings = []

        
        for parameter_name, type_expression_reference in sorted(binding_dict.items()):
            

            # TODO check parameter_name is name 
            parameter = owner.get(parameter_name)
            if not isinstance(parameter, parameter_metatype):
                print(self._source_)
                print(parameter, parameter_metatype)
                RAISE
            type_expression = type_expression_reference._resolve_()
            # TODO check subtype if not type_expression.
            
            if isinstance(parameter, metamodel.ClassParameter):
                binding_metaclass = metamodel.ClassTemplateParameterBinding
            else:
                binding_metaclass = metamodel.DataTypeTemplateParameterBinding
                
            
                
            
            
            bindings.append(binding_metaclass(parameter=parameter, type=type_expression))
            
        return bound_metatype(owner, bindings)
            



class ReferenceCall(Reference):
    def __init__(self, source: Source, *, owner: Reference, kwargs: dict):
        super().__init__(source)
        self.owner = owner
        self.kwargs = kwargs
        
    def _resolve_(self):
        owner = self.owner._resolve_()
        
        kwargs = {}
        
        
        

        
        #for parameter_name, type_expression_reference in sorted(binding_dict.items()):
            
        #    if parameter_name == 'SingleLanguageStrings':
         #       a=1
            
        
        
        
        
        
        
        
        
        
        
        
        for name, value in self.kwargs.items():
            if isinstance(value, Reference):
                # print('---------', self._source_)
                value = value._resolve_()
                
            elif isinstance(value, list):
                new_value = []
                for v in value:
                    if isinstance(v, Reference):
                        v = v._resolve_()
                    new_value.append(v)
                value = new_value
                        
                
                
                
                
            kwargs[name] = value
        
        if isinstance(owner, (metamodel.AggregatedDataType, metamodel.Class)):

            
            return owner(**kwargs)
            
        
        
        raise Exception(owner, kwargs)

        


class ElementWrapper(Reference):

    def __init__(self, source, *, namespace: WrappedNamespace, name: str):
        super().__init__(source)
        self._namespace = namespace
        self._name = name
    def _resolve_(self):
        value = self._namespace._getter_(self._name)
        if value is None:
            raise Exception(self._name)

        
        return value


# TODO begin ok





class ElementInfo(Reference):
    
    
    __slots__ = ('_macro_name_', '_metatype_', '_name_', '_owner_', '_attributes_', '_qname_',
                 '_error_', '_specification_')

    def __init__(self,
            source: Source, *,
            macro_name: T.Optional[str],
            metatype: T.Optional[T.Type[metamodel.Element]],
            name: T.Optional[str],
            owner: T.Optional[ElementInfo],
            attributes: dict[str, T.Any]) -> None:

        super().__init__(source)
        self._macro_name_ = macro_name
        self._metatype_ = metatype
        self._name_ = name
        self._owner_ = owner
        self._attributes_ = attributes

        self._qname_: T.Optional[str] = None
        self._error_: T.Optional[Message] = None
        self._specification_: T.Optional[ElementSpecification] = None



    #
    # @property
    # def source(self) -> Source:
    #     return self._source_
    #


    def _get_description_(self) -> str:
        if self._macro_name_:
            if self._name_:
                return f'{self._macro_name_} "{self._name_}"'
            else:
                return self._macro_name_
        else:
            if self._name_:
                return f'reference to "{self._name_}"'
            else:
                return f'reference'

    def _set_name_and_owner(self, name: str, owner: ElementInfo):
        if self._name_ is not None:
            RAISEERROR
        if self._owner_ is not None:
            RAISEERROR
        self._name_ = name
        self._owner_ = owner
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            calling_frame = inspect.currentframe().f_back
            calling_filename = inspect.getsourcefile(calling_frame)
            if calling_filename != __file__:
                TODO
            super(). __setattr__(name, value)
        elif isinstance(value, ElementInfo):
            value._set_name_and_owner(name, self)
        else:
            raise TypeError(f'only ElementInfos can be attributes of an ElementInfo; got {value!r}') 
    
    
    # TODO begin ok
    
    def __getattr__(self, name: str) -> ElementInfo:
        
        return ElementInfo(
            source=py_source_from_calling_frame(),
            macro_name=None,
            metatype=None,
            name=name,
            owner=self,
            attributes={})
    
    # TODO end ok

        



    def __format__(self, fmt):
        
        if not fmt.startswith('sp'):
            return super().__format__(fmt)
        fmt = fmt[2:]
        assert fmt[0] and fmt[0] in '-!~'
        if fmt[0] == '-':
            fmt = fmt[1:]
        return f'<SPREF-{id(self)}-{fmt}>'
    
    def _resolve_(self):
        specification = self._specification_
        if not specification:
            print(vars(self))
            RAISE
        return specification.resolve()
    
    
    
    


    
 

class TemplateModel(metamodel.Namespace):
    
    __slots__ = []
    
    ownedTemplates = (
        metamodel.MutableMembersProperty[metamodel.Property](
            __slots__, metamodel.Property, True,
            derived_properties=[metamodel.Namespace.ownedMembers]))
    
    def add(self, template):
        if isinstance(template, metamodel.Property):
            self.ownedTemplates.add(template)
        else:
            raise TypeError(template)


class ElementMacro:
    
    __slots__ = ('_name', '_metatype')

    def __init__(self, name: str, metatype: T.Type[metamodel.Element]) -> None:
        self._name = name
        self._metatype = metatype

    def __call__(self, **kwargs) -> ElementInfo:
        return ElementInfo(
            source=py_source_from_calling_frame(),
            macro_name=self._name,
            metatype=self._metatype,
            name=kwargs.pop('name', None),
            owner=None,
            attributes=kwargs)


def _make_macro_by_name():
    macro_by_name = {}
    for metamodel_type in [
            metamodel.AbstractDataType,
            metamodel.DataProperty,
            metamodel.Enumeration,
            metamodel.EnumerationLiteral,
            metamodel.Model,
            metamodel.Package,
            metamodel.AbstractClass,
            metamodel.ConcreteClass,
            metamodel.ReferenceProperty,
            metamodel.AggregatedDataType,
            metamodel.CompositionProperty,
            metamodel.DataTypeParameter,
            metamodel.ClassParameter,
            TemplateModel]:

        # E.g.: ConcreteClass -> "CONCRETE_CLASS"
        name = '_'.join(
            word.upper() for word in re.findall('[A-Z][^A-Z]*', metamodel_type.__name__))
        macro_by_name[name] = ElementMacro(name, metamodel_type)
    return macro_by_name

MACRO_BY_NAME = _make_macro_by_name()



class Rdl2Namespace:
    
    def __getattr__(self, name):
        return JordName(name.replace('_', ' '))
    
    def term(self, name):
        return Rdl2Name(name)
    
    
class Rdl2Name(str):
    
    def get_uri_label_and_description(self, rdl_data):
        
       # rdl_data = rdl_data.get('RDL
        
        result = rdl_data.get(str(self))
        if result:
            return result

        query_code = f'''
            SELECT ?uri ?definition
            WHERE {{
              SERVICE <https://data.posccaesar.org/rdl/sparql> {{
                ?uri <http://www.w3.org/2000/01/rdf-schema#label> {rdflib.Literal(self).n3()} .
                OPTIONAL {{ ?uri <http://data.posccaesar.org/rdl/hasDefinition> ?definition }}
              }}
            }}'''
        
        rows = list(rdflib.Graph().query(query_code))
        if not rows:
            raise Exception(label)
        elif len(rows) > 1:
            raise Exception(label, rows)
        else:
            uri, definition = rows[0]
            uri = str(uri)
            definition = str(definition)
          
        result = uri, str(self), str(definition)
        rdl_data[str(self)] = result

        return result

class JordNamespace:
    
    def __getattr__(self, name):
        return JordName(name.replace('_', ' '))
    
    def term(self, name):
        return JordName(name)

class JordName(str):
    
    def get_uri_label_and_description(self, all_rdl_data):
        
        rdl_data = all_rdl_data.get('jord')
        if rdl_data is None:
            rdl_data = {}
            all_rdl_data['jord'] = rdl_data

        result = rdl_data.get(str(self))
        if result:
            return result

        query_code = f'''
            SELECT ?uri ?definition
            WHERE {{
              SERVICE <https://data.posccaesar.org/rdl/sparql> {{
                ?uri <http://www.w3.org/2000/01/rdf-schema#label> {rdflib.Literal(self).n3()} .
                OPTIONAL {{ ?uri <http://data.posccaesar.org/rdl/hasDefinition> ?definition }}
              }}
            }}'''
        
        rows = list(rdflib.Graph().query(query_code))
        if not rows:
            raise Exception(label)
        elif len(rows) > 1:
            raise Exception(label, rows)
        else:
            uri, definition = rows[0]
            uri = str(uri)
            definition = str(definition)
          
        result = uri, str(self), str(definition)
        rdl_data[str(self)] = result

        return result


class DexpiNamespace:
    
    def __getattr__(self, name):
        return DexpiName(name.replace('_', ' '))
    
    def term(self, name):
        return DexpiName(name)


class DexpiName(str):
    
    def get_uri_label_and_description(self, rdl_data):
        namespace = 'http://sandbox.dexpi.org/rdl/'
        return namespace + cap_to_camel_case(self), str(self), None














class TODO_MACRO:
    def __getattr__(self, name):
        pass
    def term(self, name):
        pass
    




AUTO = object()






class WrappedNamespace:
    
    def __init__(self, name: str, getter):
        
        self._name_ = name
        self._getter_ = getter
        
    
    def __getattr__(self, name):
        return ElementWrapper(
            py_source_from_calling_frame(),
            namespace=self,
            name=name)
        
        

BUILTIN = WrappedNamespace('BUILTIN', {
    'AnyURI': metamodel.BUILTIN.AnyURI,
    'Boolean': metamodel.BUILTIN.Boolean,
    'DateTime': metamodel.BUILTIN.DateTime,
    'Double': metamodel.BUILTIN.Double,
    'Integer': metamodel.BUILTIN.Integer,
    'String': metamodel.BUILTIN.String,
    'Undefined': metamodel.BUILTIN.Undefined,
    'UnsignedByte': metamodel.BUILTIN.UnsignedByte}.get)










MACRO_BY_NAME.update(dict(
  
  
    BUILTIN = BUILTIN,

    AUTO=AUTO,
    TODO=print,
    WARNING=print,
    ERROR=print,
    FATAL_ERROR=print,
    JORD_RDL=JordNamespace(),
    RDL2=Rdl2Namespace(),
    DEXPI_RDL=DexpiNamespace()))


MEMBER_METATYPES_BY_METATYPE: dict[T.Type[metamodel.Element], tuple[T.Type[metamodel.NamedElement], ...]] = {
    metamodel.AbstractClass: (metamodel.Property, metamodel.TypeParameter),
    metamodel.AbstractDataType: (metamodel.AbstractDataType, ),
    metamodel.AggregatedDataType: (metamodel.DataProperty, metamodel.DataTypeParameter),
    metamodel.ConcreteClass: (metamodel.Property, metamodel.TypeParameter),
    metamodel.Enumeration: (metamodel.Type, metamodel.EnumerationLiteral),
    metamodel.Model: (metamodel.Type, metamodel.Package, metamodel.SingletonValue),
    metamodel.Package: (metamodel.Type, metamodel.Package, metamodel.SingletonValue),
    TemplateModel: (metamodel.Property, )}


class TempTemplate:
    
    def __getattr__(self, name):
        return name


TEMP_TEMPLATE = lambda: TempTemplate()


class SpNamespace:
    
    def __init__(self, members: dict):
        self.__dict__.update(members)

    def __getitem__(self, name):
        return self.__dict__[name]
    
    def __setitem__(self, name, value):
        if 0 and TODO and (isinstance(value, ElementInfo) and value._metatype_ is metamodel.Model
                or isinstance(value, Templates)):
            if name in self.__dict__:
                ERROR
            value._set_name_and_owner(name, None)
        self.__dict__[name] = value
    
    def __iter__(self):
        return iter(self.__dict__)
    
    def __len__(self):
        return len(self.__dict__)


class DslReader:

    def __init__(self,
            src: str | Path | T.Iterable[str|Path],
            cache_dir: T.Optional[Path]=None) -> None:

        # TOLATERDO: move to separate util
        # TOLATERDO: make class rather than instance attribute
        rdl_data = {}
        if cache_dir:
            rdl_data_path = cache_dir / 'rdl_data.json'
            if rdl_data_path.exists():
                # pylint: disable=broad-exception-caught
                try:
                    with rdl_data_path.open('r') as fin:
                        rdl_data = json.load(fin)
                except Exception as error:
                    print(error) # TODO log

            def save(rdl_data=rdl_data, rdl_data_path=rdl_data_path):
                # pylint: disable=dangerous-default-value
                # pylint: disable=broad-exception-caught
                try:
                    rdl_data_path.parent.mkdir(parents=True, exist_ok=True)
                    with rdl_data_path.open('w') as fout:
                        json.dump(rdl_data, fout, sort_keys=True, indent=4)
                except Exception as error:
                    print(error) # TODO log
            atexit.register(save)
        self.rdl_data = rdl_data

        self.messages: list[Message] = []

        # TODO: remove
        self.model_by_name: dict[str, metamodel.Model] = {
            'Builtin': metamodel.BUILTIN}
        self.templates_by_name: dict[str, TemplateModel] = {}
        self.metadata = metamodel.MetaData(
            name='MetaData',
            uri='https://data.dexpi.org/models/2.0.0/MetaData.xml')
        self.index_by_path = {}

        LOGGER.info('read sources')
        references = self._read_sources(src)
        LOGGER.info('build models')
        element_infos = [info for info in references if isinstance(info, ElementInfo)]
        element_infos = self._element_infos_with_qname(element_infos)
        element_specifications = self._build_element_specifications(element_infos)
        self._build_elements(element_specifications)
        LOGGER.info('%s models built:', len(self.model_by_name)-1)
        for name in sorted(self.model_by_name):
            if name != 'Builtin':
                LOGGER.info('- %s', name)
                
        self.model_set = metamodel.ModelSet()
        for model in self.model_by_name.values():
            self.model_set.add(model)
            
        self.model_set.add(self.metadata)
            

    def _add_message(self, message: Message) -> None:
        assert message.nr is None
        self.messages.append(message)
        message.nr = len(self.messages)
        LOGGER.warning(message)

    def _iter_src(self, src: str | Path | T.Iterable[str|Path]) -> T.Iterator[str|Path]:
        if isinstance(src, (str, Path)):
            src = [src]
        for single_src in src:
            if isinstance(single_src, str):
                yield single_src
            elif single_src.is_file():
                yield single_src
            elif single_src.is_dir():
                yield from single_src.rglob('*.py')

    def _read_sources(self, src: str | Path | T.Iterable[str|Path]) -> list[Reference]:

        Reference.track_instances()

        try:
            for single_src in self._iter_src(src):
                LOGGER.info('- read %s', single_src)
                local_vars = SpNamespace(MACRO_BY_NAME)
                local_vars.NAMESPACE = local_vars
                if isinstance(single_src, Path):
                    code = compile(single_src.read_bytes(), str(single_src), 'exec')
                    local_vars.__file__ = str(single_src)
                    local_vars.THIS_DIR = single_src.parent
                else:
                    code = compile(single_src, '<string>', 'exec')
                exec(code, None, local_vars)
        except Exception as error:
            traceback_lines = traceback.format_exc().splitlines()
            del traceback_lines[1]
            del traceback_lines[1]
            msg = FatalErrorMessage('\n'.join(traceback_lines))
            self._add_message(msg)
            Reference.get_instances()
            return []
        else:
            return Reference.get_instances()


    def _element_infos_with_qname(self, infos: list[ElementInfo]) -> list[ElementInfo]:

        msg: ErrorMessage

        infos_to_handle: list[ElementInfo] = []
        for info in infos:
            name = info._name_
            if not isinstance(name, (str, type(None))):
                msg = InvalidParameterType([info], 'name', name, (str, type(None)))
                info._error_ = msg
                self._add_message(msg)
                continue
            if isinstance(name, str) and not IDENTIFIER_PATTERN.match(name):
                msg = NoValidIdentifier([info], 'name', name)
                info._error_ = msg
                self._add_message(msg)
                continue
            if name is None and (
                    info._owner_ or info._metatype_ in (metamodel.Model, TemplateModel)):
                # Case 'no owner' is handled below.
                msg = MissingParameter([info], 'name')
                info._error_ = msg
                self._add_message(msg)
                continue
            infos_to_handle.append(info)

        progress_made = True
        infos_with_qname: list[ElementInfo] = []
        while progress_made:
            progress_made = False
            infos = infos_to_handle
            infos_to_handle = []

            for info in infos:
                owner = info._owner_
                if owner is None:
                    if info._metatype_ in (metamodel.Model, TemplateModel):
                        info._qname_ = info._name_
                        infos_with_qname.append(info)
                    else:
                        msg = NoOwner(info)
                        info._error_ = msg
                        self._add_message(msg)
                    progress_made = True
                elif owner._error_:
                    msg = OwnerSkipped([info], [owner])
                    info._error_ = msg
                    self._add_message(msg)
                    progress_made = True
                elif owner._qname_:
                    info._qname_ = owner._qname_ + f'.{info._name_}'
                    infos_with_qname.append(info)
                else:
                    infos_to_handle.append(info)
            infos = infos_to_handle

        assert not infos_to_handle

        return infos_with_qname


    def _build_element_specifications(self, infos: list[ElementInfo]) -> list[ElementSpecification]:

        infos_by_qname: dict[str, list[ElementInfo]] = {}
        for info in infos:
            assert info._qname_
            infos_by_qname.setdefault(info._qname_, []).append(info)

        specifications: list[ElementSpecification] = []
        for qname, infos_with_qname in sorted(infos_by_qname.items()):
            specification = self._build_element_specification(qname, infos_with_qname)
            if specification:
                specifications.append(specification)

        return specifications


    def _build_element_specification(self,
            qname: str, infos: list[ElementInfo]) -> T.Optional[ElementSpecification]:

        msg: ErrorMessage

        metatypes = set()
        for info in infos:
            if info._metatype_:
                metatypes.add(info._metatype_)
        if not metatypes:
            msg = MissingMetatype(infos)
            for info in infos:
                info._error_ = msg
            self._add_message(msg)
            return None
        if len(metatypes) > 1:
            msg = MultipleMetatypes([info for info in infos if info._metatype_], metatypes)
            for info in infos:
                info._error_ = msg
            self._add_message(msg)
            return None

        metatype = metatypes.pop()
        metatype_infos = [info for info in infos if info._metatype_]

        owner_info = infos[0]._owner_
        owner_specification: T.Optional[ElementSpecification] = None
        # TOLATERDO: Do why need to check anything for Model, TemplateModel?
        if metatype not in (metamodel.Model, TemplateModel):
            assert owner_info
            owner_specification = owner_info._specification_
            if owner_specification:
                if not issubclass(
                        metatype,
                        MEMBER_METATYPES_BY_METATYPE.get(owner_specification.metatype, ())):
                    msg = InvalidMemberType(infos, metatype, owner_specification.metatype)
                    for info in infos:
                        info._error_ = msg
                    self._add_message(msg)
                    return None
            else:
                owner_infos = []
                for info in infos:
                    assert info._owner_
                    owner_infos.append(info._owner_)
                msg = OwnerSkipped(infos, owner_infos)
                for info in infos:
                    info._error_ = msg
                self._add_message(msg)
                return None

        infos_by_attribute_name: dict[str, list[ElementInfo]] = {}
        for info in infos:
            for attribute_name in info._attributes_:
                infos_by_attribute_name.setdefault(attribute_name, []).append(info)

        value_by_attribute_name: dict[str, T.Any] = {}
        error_by_attribute_name: dict[str, Message] = {}
        for attribute_name, attribute_infos in infos_by_attribute_name.items():
            if len(attribute_infos) > 1:
                msg = MultipleParameterValues(attribute_infos, attribute_name)
                error_by_attribute_name[attribute_name] = msg
                self._add_message(msg)
            else:
                value_by_attribute_name[attribute_name] = (
                    attribute_infos[0]._attributes_[attribute_name])

        specification = ElementSpecification(
            qname=qname,
            infos=infos,
            owner_specification=owner_specification,
            metatype=metatype,
            metatype_infos=metatype_infos,
            value_by_attribute_name=value_by_attribute_name,
            infos_by_attribute_name=infos_by_attribute_name,
            error_by_attribute_name=error_by_attribute_name)
        for info in infos:
            info._specification_ = specification
        if owner_specification:
            owner_specification.owned_specifications.append(specification)

        return specification


    def _build_elements(self, element_specifications: list[ElementSpecification]) -> None:
        
        msg: ErrorMessage
        
        self._metadata_cache = []

        type_specifications: list[ElementSpecification] = []
        specifications_by_priority: dict[int, list[ElementSpecification]] = {}

        for spec in element_specifications:
            specifications_by_priority.setdefault(spec.get_priority(), []).append(spec)
            if issubclass(spec.metatype, metamodel.Type):
                type_specifications.append(spec)

        types_and_template_usages = []

        for priority, specifications in sorted(specifications_by_priority.items()):

            progress_made = True
            while progress_made:
                progress_made = False
                to_build: list[ElementSpecification] = []
                for spec in specifications:
                    try:
                        element = spec.build(self)
                        assert element, spec.metatype
                        progress_made = True
                        if isinstance(element, metamodel.Model):
                            assert element.name not in self.model_by_name
                            self.model_by_name[element.name] = element
                        elif isinstance(element, TemplateModel):
                            assert element.name not in self.templates_by_name
                            self.templates_by_name[element.name] = element
                        self._add_metadata(element, spec.value_by_attribute_name, 
                                           spec.infos_by_attribute_name, spec.metatype_infos[0]._source_)
                    except Postpone:
                        to_build.append(spec)
                specifications = to_build
                
            if specifications:
                msg = CyclicDependency(specifications)
                for specification in specifications:
                    assert specification.element is None
                    assert specification.error is None
                    specification.error = msg
                self._add_message(msg)

        for spec in type_specifications:
            type_element = spec.element
            if not type_element:
                continue

            if (template_usages := spec.value_by_attribute_name.get('templates')) is not None:

                if not isinstance(template_usages, list):
                    msg = InvalidParameterType(
                        spec.infos_by_attribute_name['templates'],
                        'templates',
                        template_usages,
                        (list, ))
                    self._add_message(msg)
                    continue

                for usage_nr, usage in enumerate(template_usages):
                    if not isinstance(usage, ElementInfo):
                        msg = InvalidParameterType(
                            spec.infos_by_attribute_name['templates'],
                            f'templates[{usage_nr}]',
                            usage,
                            (metamodel.Property, ))
                        self._add_message(msg)
                        continue

                    if usage._error_:
                        msg = SkippedElementUsed(
                            spec.infos_by_attribute_name['templates'],
                            f'templates[{usage_nr}]',
                            usage._qname_,
                            causes=[usage._error_])
                        self._add_message(msg)
                        continue

                    assert usage._specification_
                    prop = usage._specification_.element
                    if not isinstance(prop, metamodel.Property):
                        msg = InvalidParameterType(
                            spec.infos_by_attribute_name['templates'],
                            f'templates[{usage_nr}]',
                            prop,
                            (metamodel.Property, ))
                        self._add_message(msg)
                        continue

                    prop_kwargs = {
                        'name': prop.name,
                        'lower': prop.lower,
                        'upper': prop.upper,
                        'type_': prop.type,
                        'isOrdered': prop.isOrdered}
                    
                    if isinstance(prop, metamodel.DataProperty):
                        prop_kwargs['isUnique'] = prop.isUnique
                    elif isinstance(prop, metamodel.ReferenceProperty):
                        prop_kwargs['isUnique'] = prop.isUnique
                        prop_kwargs['oppositeLower'] = prop.oppositeLower
                        prop_kwargs['oppositeUpper'] = prop.oppositeUpper
                    new_prop = type(prop)(**prop_kwargs)
                    type_element.add(new_prop)
                    self._add_metadata(new_prop, usage._specification_.value_by_attribute_name,
                                       usage._specification_.infos_by_attribute_name, usage._specification_.metatype_infos[0]._source_)

    
        for args in self._metadata_cache:
            assert args[0]
            self._do_add_metadata(*args)

        
    def _add_metadata(self, element, value_by_attribute_name, infos_by_attribute_name, source):
        
        self._metadata_cache.append((element, value_by_attribute_name, infos_by_attribute_name, source))
        
        
    def _do_add_metadata(self, element, value_by_attribute_name, infos_by_attribute_name, source):
        
        

        #doc = self.value_by_attribute_name.get('doc')
        #if isinstance(doc, str):
        #    metadata.set(element, 'doc', doc)
            
        import textwrap
        
            
        for name in ['rdl_uri', 'rdl_label', 'un_symbol', 'un_code', 'description', 'doc', 'details']:
            value = value_by_attribute_name.get(name)
            

            if isinstance(value, str):
                
                if name in ['details', 'description', 'doc']:
                    
                    
                    if name == 'doc':
                        assert 'description' not in value_by_attribute_name, element
                        name = 'description'
                    
                    value = textwrap.dedent(value).strip()
                    
                    if 'SELF' in value:
                        assert isinstance(element, (metamodel.Type, metamodel.Package, metamodel.Model)), element.qualifiedName
                        def on_self(matchobj):
                            nolink = matchobj.group('nolink')
                            path = matchobj.group('path')
                            return f':sp:element:`{nolink}~{element.qualifiedName}{path}`'
                        value = re.sub(
                            r'\<(?P<nolink>\!?)SELF(?P<path>[^\>]*)\>',
                            on_self,
                            value)
                        
                    if 'OWNER' in value:
                        assert isinstance(element, (metamodel.Property, metamodel.TypeParameter)), element.qualifiedName
                        def on_owner(matchobj):
                            nolink = matchobj.group('nolink')
                            path = matchobj.group('path')
                            return f':sp:element:`{nolink}~{element.owner.qualifiedName}{path}`'
                        value = re.sub(
                            r'\<(?P<nolink>\!?)OWNER(?P<path>[^\>]*)\>',
                            on_owner,
                            value)
                        
                    if 'SPREF' in value:
                        ko
                        
                        # TODO: still used?

                        def on_spref(matchobj):
                            info_nr = matchobj.group('info_nr')
                            modifier = matchobj.group('modifier')
                            path = matchobj.group('path')

                            assert modifier in ('', '!', '~', '!~', '~!')
                            if path:
                                assert path[0] != '.'
                                path = '.' + path
                                
                                
                            base_info = element_info_by_id[info_nr]
                            base_path = base_info._qname_ # TODO handle None
                            assert base_path

                            return f':sp:element:`{modifier}{base_path}{path}`'

                        value = re.sub(
                            r'\<SPREF-(?P<info_nr>[0-9]*)-(?P<modifier>[\~\!]*)(?P<path>[^\>]*)\>',
                            on_spref,
                            value)
                        
                        
                    if 'image' in value:
                     #   .. image:: example1.*
                     
                      

                        
                        
                        def on_image(matchobj):
                            
                            src_infos = infos_by_attribute_name.get(name)
                            assert len(src_infos) == 1
                        
                            
                            
                            src_dir = src_infos[0]._source_.path.parent
     
                            file_name = matchobj.group('file_name')
                            if file_name.endswith('.*'):
                                file_name = file_name[:-2] + '.svg'
                            file_path = src_dir / file_name

                            if not file_path.is_file():
                                return '???' # TODO

                            file_path = str(file_path)
                            
                            index = self.index_by_path.get(file_path)
                            if index is None:
                                index = len(self.index_by_path)
                                self.index_by_path[file_path] = index
                                
                            return f'.. image:: /images/img{index}.*'


                        value = re.sub(
                            r'\.\. image:: (?P<file_name>.*?)$',
                            on_image,
                            value,
                            flags=re.MULTILINE)
       

                self.metadata.set(element, name, value)
                
                
        
        rdl = value_by_attribute_name.get('rdl')
        if rdl is not None:
            rdl_uri, rdl_label, rdl_definition = rdl.get_uri_label_and_description(self.rdl_data)
            assert self.metadata.get(element, 'rdl_uri', None) is None
            assert self.metadata.get(element, 'rdl_label', None) is None
            self.metadata.set(element, 'rdl_uri', rdl_uri)
            self.metadata.set(element, 'rdl_label', rdl_label)
            
            
            if value_by_attribute_name.get('description') is AUTO:
                self.metadata.set(element, 'description', rdl_definition)
                self.metadata.set(element, 'description_from_rdl', True)
        else:
            if value_by_attribute_name.get('description') is AUTO:
                print(element)
                # TODO ERROR
            
                
        exampleValue = value_by_attribute_name.get('exampleValue')
        if exampleValue is not None:
            if isinstance(exampleValue, (str, datetime.datetime, int, float)):
                nr_of_values = 1
            
            elif isinstance(exampleValue, Reference):
                exampleValue = exampleValue._resolve_()
                assert isinstance(exampleValue, (metamodel.Object, metamodel.AggregatedDataValue, metamodel.EnumerationLiteral)), exampleValue
                nr_of_values = 1
            elif isinstance(exampleValue, list):
                tempValue = []
                for item in exampleValue:
                    if isinstance(item, (str, datetime.datetime, int, float)):
                        pass
                    elif isinstance(item, Reference):
                        item = item._resolve_()
                        assert isinstance(item, (metamodel.Object, metamodel.AggregatedDataValue, metamodel.EnumerationLiteral)), exampleValue
                    tempValue.append(item)
                exampleValue = tempValue
                nr_of_values = len(exampleValue)
            else:
                raise Exception(exampleValue)
            
            
            if nr_of_values < element.lower:
                print('###', source)
                print('### need', element.lower, 'values for ', element.qualifiedName)
                exampleValue = None
            if element.upper is not None and element.upper < nr_of_values:
                print('###', source)
                print('### need at most', element.upper, 'values for ', element.qualifiedName)
                exampleValue = None
                
            if nr_of_values == 1 and (element.upper is None or element.upper > 1) and not isinstance(exampleValue, list):
                exampleValue = [exampleValue]

                
                #print('###', source)
                #print('### need a list for ', element.qualifiedName)
                
                
            if exampleValue is not None:
                self.metadata.set(element, 'exampleValue', exampleValue)
   
            
        elif isinstance(element, metamodel.DataProperty):
            
            if 'Process' not in element.qualifiedName:
                pass
            
              #  print('###', source)
              #  print('### no example property for', element.qualifiedName)



class Postpone(Exception):
    pass


class ElementSpecification:
    def __init__(self,
            qname: str,
            infos: list[ElementInfo],
            owner_specification: T.Optional[ElementSpecification],
            metatype: T.Type[metamodel.Element],
            metatype_infos: list[ElementInfo],
            value_by_attribute_name: dict[str, T.Any],
            infos_by_attribute_name: dict[str, list[ElementInfo]],
            error_by_attribute_name: dict[str, Message]):
        
        self.name = qname.rsplit('.', 1)[-1]
        self.qname = qname
        self.infos = infos
        self.owner_specification = owner_specification
        self.metatype = metatype
        self.metatype_infos = metatype_infos
        self.owned_specifications: list[ElementSpecification] = []
        self.value_by_attribute_name = value_by_attribute_name
        self.infos_by_attribute_name = infos_by_attribute_name
        self.error_by_attribute_name = error_by_attribute_name
        self.element: T.Optional[metamodel.NamedElement] = None
        self.error: T.Optional[Message] = None

        
    def resolve(self):
        if self.error:
            RAISE
        element = self.element
        if not self.element:
            print('#########', self.qname)
            raise Postpone()
        return element
        
        
        
        
    property_priority = 6
        
        
    def get_priority(self) -> int:
        for priority, metatype in enumerate([
                metamodel.Model,
                metamodel.Package,
                metamodel.Type,
                metamodel.TypeParameter,
                TemplateModel,
                metamodel.EnumerationLiteral,
                metamodel.Property]):

            if issubclass(self.metatype, metatype):
                return priority
        raise Exception(self.metatype)
    
    
    
    def _get_required_attribute(self, attribute_name: str, reader: DslReader):
        value = self.value_by_attribute_name.get(attribute_name, _NOT_GIVEN)
        if value is _NOT_GIVEN:
            error_msg = self.error_by_attribute_name.get(attribute_name)
            if error_msg:
                COV
            else:
                COV
        return value
    
    
    
    def _get_required_uri_attribute(self, attribute_name: str, reader: DslReader):
        
        uri = self._get_required_attribute(attribute_name, reader)
        if not isinstance(uri, str):
            COV
        # TOLATERDO: check pattern?
        return uri
        
        
    def _get_type_attributes(self, attribute_name):
        
        

       
        
        if attribute_name in self.error_by_attribute_name:
            return []  # TODO
        type_specifications = self.value_by_attribute_name.get(attribute_name, [])
        types = [ts._specification_.element for ts in type_specifications]
        if None in types:
            raise Postpone()
        return types
    
    
    def _get_non_negative_integer_attribute(self, attribute_name):
        value = self.value_by_attribute_name.get(attribute_name)
        assert isinstance(value, int)
        assert value >= 0
        return value
    
    def _get_optional_non_negative_integer_attribute(self, attribute_name):
        value = self.value_by_attribute_name.get(attribute_name)
        assert value is None or isinstance(value, int)
        assert value is None or value >= 0
        return value
    
    def _get_optional_bool_attribute(self, attribute_name):
        value = self.value_by_attribute_name.get(attribute_name)
        assert value is None or isinstance(value, bool)
        return value

    
    
    
    
    
    
    
    
    def _get_type_expression_attribute(self, attribute_name):
        if attribute_name in self.error_by_attribute_name:
            RAISE
            
        type_expression_reference = self.value_by_attribute_name.get(attribute_name, None)
        
        if type_expression_reference is None:
            RAISE
            
        if not isinstance(type_expression_reference, Reference):
            RAISE
            
        
            
        type_expression = type_expression_reference._resolve_()
        
        #if not isinstance(type_expression, metamodel.TypeExpression):
        #    RAISE
        
        
        return type_expression

            
        

        
        
        
    def get_owner_element(self, reader: DslReader) -> T.Optional[ElementSpecification]:
        owner_specification = self.owner_specification
        if self.metatype in (metamodel.Model, TemplateModel):
            assert not owner_specification
            return None
        assert owner_specification
        if owner_specification.error:
            assert owner_specification.element is None
            RAISE
        return owner_specification.element
        
        
        
        
    def build(self, reader: DslReader):
        
        owner_element = self.get_owner_element(reader)
        
        if self.metatype is metamodel.Model:
            assert not owner_element
            build_element = self._build_model
        elif self.metatype is TemplateModel:
            assert not owner_element
            build_element = self._build_templates
        elif not owner_element:
            build_element = None
        elif self.metatype is metamodel.Package:
            build_element = self._build_package
        elif issubclass(self.metatype, metamodel.Type):
            build_element = self._build_type
        elif issubclass(self.metatype, metamodel.TypeParameter):
            build_element = self._build_type_parameter
        elif issubclass(self.metatype, metamodel.Property):
            build_element = self._build_property
        elif issubclass(self.metatype, metamodel.EnumerationLiteral):
            build_element = self._build_enumeration_literal
        else:
            return None and TODORAISE
            raise Exception(self.metatype)
              
        if build_element:
            element = build_element(reader)
            if element:
                self.element = element
                if owner_element:
                    # E.g., EnumerationLiterals are added to their Enumerations during construction.
                    if element.owner is not owner_element:
                        owner_element.add(element)
        else:
            element = None
                
        return element

    def _build_model(self, reader: DslReader) -> metamodel.Model:
        uri = self._get_required_uri_attribute('uri', reader)
        return metamodel.Model(name=self.name, uri=uri)
    
    def _build_templates(self, reader: DslReader) -> TemplateModel:
        return TemplateModel(name=self.name)
        
    def _build_package(self, reader: DslReader) -> metamodel.Package:
        return metamodel.Package(name=self.name)
    
    def _build_enumeration_literal(self, reader) -> metamodel.EnumerationLiteral:
        owner_element = self.get_owner_element(reader)
        assert isinstance(owner_element, metamodel.Enumeration)
        # TODO: how to keep order?
        return metamodel.EnumerationLiteral(name=self.name, enumeration=owner_element)
    
    def _build_type(self, reader: DslReader):
 
        super_types = self._get_type_attributes('superTypes')
        
        metatype = self.metatype
        if issubclass(metatype, metamodel.Class):
            super_type_metatype = metamodel.Class
        else:
            assert issubclass(metatype, metamodel.DataType)
            super_type_metatype = metamodel.AbstractDataType
            
        invalid_super_types = [
            super_type for super_type in super_types
            if not isinstance(super_type, super_type_metatype)]
        if invalid_super_types:
            RAISE

        return metatype(name=self.name, superTypes=super_types)
    
    
    def _build_type_parameter(self, reader: DslReader):
        
        # TODO: rename type -> baseType
        
        type_expression = self._get_type_expression_attribute('type')
        0 and RAISE # check param?
        
        return self.metatype(name=self.name, type=type_expression)
        
    
    
    def _build_property(self, reader: DslReader):


        metatype = self.metatype
        type_expression = self._get_type_expression_attribute('type')

        0 and RAISE # check param
        if issubclass(metatype, metamodel.DataProperty):
            if not isinstance(type_expression, metamodel.DataTypeExpression):
                ko
        else:
            assert issubclass(metatype, metamodel.ObjectProperty)
            if not isinstance(type_expression, metamodel.ClassExpression):
                ko
                
        prop_kwargs = {
            'name': self.name,
            'type_': type_expression,
            'lower': self._get_non_negative_integer_attribute('lower'),
            'upper': self._get_optional_non_negative_integer_attribute('upper'),
            'isOrdered': self._get_optional_bool_attribute('isOrdered') or False}
        
        if metatype in [metamodel.DataProperty, metamodel.ReferenceProperty]:
            prop_kwargs['isUnique'] = self._get_optional_bool_attribute('isUnique') or False

            
            
        if metatype is metamodel.ReferenceProperty:
            prop_kwargs['oppositeLower'] = self._get_non_negative_integer_attribute('oppositeLower')
            prop_kwargs['oppositeUpper'] = self._get_optional_non_negative_integer_attribute('oppositeUpper')
 
        return metatype(**prop_kwargs)


# TODO: move
            
def cap_to_camel_case(cap_case: str):
    parts: list[str] = []
    cap = True
    for char in cap_case:
        if char.strip():
            if not cap:
                char = char.lower()
            else:
                cap = False
            parts.append(char)
        else:
            cap = True
    return ''.join(parts)



# TODO -> TOLATERDO
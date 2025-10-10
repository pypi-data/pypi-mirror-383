from collections import namedtuple
import csv
import pathlib
import re
import typing as T

from pnb.mcl.utils import SYMBOL_PATTERN
import ezodf



UomLiteral = namedtuple('UomLiteral', ['row_index',
                                       'rdl_uri',
                                       'rdl_label',
                                       'name',
                                       'un_symbol',
                                       'alt_symbol',
                                       'un_code',
                                       'comment'])


# TODO: move
def cap_case(camel_case: str):
    parts: list[str] = []
    for char in camel_case:
        if char.isupper() and parts:
            parts.append('_')
            parts.append(char)
        else:
            parts.append(char.upper())

    return ''.join(parts)

def dimension_to_rst(dimension: str) -> str:
    if dimension == 1.0:
        return '1'
    for old, new in (
            ('\u207b', '-'),
            ('\u00b9', '1'),
            ('\u00b2', '2'),
            ('\u00b3', '3')):
        dimension = dimension.replace(old, new)

    superscript_chars = '0123456789-'

    # Split in parts that are either supercripted or not.
    parts = re.findall(
        '(?:[{}]+)|(?:[^{}]+)'.format(
            superscript_chars, superscript_chars),
        dimension)

    # TODO: make error invalid dimension
    assert dimension == ''.join(parts)

    fragments = []
    for part in parts:
        if set(part).issubset(superscript_chars):
            fragments.append(f':sup:`{part}`')
        else:
            assert set(part).isdisjoint(superscript_chars)
            fragments.append(part)

    return '\\ '.join(fragments)





def camel_to_normal(text):
    
    # TODO?
    if text == 'pH':
        return text
    
    assert ' ' not in text, text
    result = []
    for char in text:
        if char.isupper():
            if result:
                result.append(' ')
            char = char.lower()
        result.append(char)
    return ''.join(result)

class PhysicalQuantityType:

    def __init__(self, src: str, row_index: int,
                 raw_name: T.Any, physical_dim: T.Any, rdl_uri: T.Any, comment: T.Any):
        self.src = src
        self.row_index = row_index
        self.raw_name = raw_name
        self.physical_dim = physical_dim
        self.rdl_uri = rdl_uri
        self.comment = comment

    def check_args(self, namespace, package):
        ok = True
        if not isinstance(self.raw_name, str):
            ok = False
            namespace.ERROR(self.src, self.row_index,
                            f'{self.raw_name!r} must be a string')
        elif not SYMBOL_PATTERN.fullmatch(self.raw_name):
            ok = False
            namespace.ERROR(self.src, self.row_index,
                            f'{self.raw_name!r} must have pattern of a symbol')
        elif not (isinstance(self.physical_dim, str) or self.physical_dim==1.0):
            ok = False
            namespace.ERROR(self.src, self.row_index,
                            f'{self.physical_dim!r} must be a string or the float 1.0')
        elif not (isinstance(self.rdl_uri, str) or self.rdl_uri is None):
            ok = False
            namespace.ERROR(self.src, self.row_index,
                            f'{self.rdl_uri!r} must be a string or None')
            # TODO: check https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not
        return ok

    def create(self, namespace, package):
        raise NotImplementedError()

class PhysicalQuantityTypeTemplate(PhysicalQuantityType):

    def __init__(self, uom_literals: list[UomLiteral], description: T.Any, **kwargs):
        super().__init__(**kwargs)
        self.uom_literals = uom_literals
        self.description = description

    def check_args(self, namespace, package):
        ok = super().check_args(namespace, package)
        if not self.uom_literals:
            namespace.WARNING(self.src, self.row_index,
                            f'{self.raw_name!r} has no literals')
        elif not (isinstance(self.description, str) or self.description is None):
            ok = False
            namespace.ERROR(self.src, self.row_index,
                            f'{self.description!r} must be a string or None')

        return ok

    def create(self, namespace, package, s_types=()):
        if not self.check_args(namespace, package):
            return

        # super types not empty for application area types
        # name = f'Nullable{self.raw_name}'
        # abstract_data_type = namespace.ABSTRACT_DATA_TYPE(
        #     superTypes=s_types, description=self.getdoc_for_nullable_type())
        # setattr(package, name, abstract_data_type)
        #
        # name = f'{self.raw_name}'
        # aggregated_data_type = namespace.AGGREGATED_DATA_TYPE(
        #     superTypes=[abstract_data_type], description=self.getdoc_for_type())
        # setattr(package, name, aggregated_data_type)

        name = f'{self.raw_name}Unit'
        
        
        if not s_types:
            s_types = [package.PhysicalQuantityUnit]
            
        enum = namespace.ENUMERATION(
            description=self.getdoc_for_enum(),
            superTypes=s_types)
        setattr(package, name, enum)
        
        for lit in self.uom_literals:
            if not SYMBOL_PATTERN.fullmatch(lit.name):
                #TODO: row index
                namespace.ERROR(self.src, 0,
                                f'{lit.name!r} must have pattern of a symbol')
                continue
            setattr(enum, lit.name, namespace.ENUMERATION_LITERAL(
                rdl_uri=lit.rdl_uri,
                rdl_label=lit.rdl_label,
                un_symbol=lit.un_symbol,
                un_code=lit.un_code))


    def getdoc_for_nullable_type(self):
        raise NotImplementedError()



    def getdoc_for_enum(self):
        # TODO: link for dimension
        return f'''
            A unit of measurement for a physical quantity of type *{camel_to_normal(self.raw_name)}* with dimension
            {dimension_to_rst(self.physical_dim)}.'''

    def getdoc_for_null_value(self):
        REM

class SimplePhysicalQuantityType(PhysicalQuantityTypeTemplate):
    pass


class ApplicationAreaPhysicalQuantityType(PhysicalQuantityTypeTemplate):

    def __init__(self, application_area: str, super_type_name: str, **kwargs):
        super().__init__(**kwargs)
        self.application_area = application_area
        self.super_type_name = super_type_name

    def check_args(self, namespace, package):
        ok = super().check_args(namespace, package)
        if not isinstance(self.application_area, str):
            ok = False
            namespace.ERROR(self.src, self.row_index,
                            f'{self.application_area!r} must be a string')

        return ok

    def getdoc_for_nullable_type(self):
        REM
        

class ApplicationDependentPhysicalQuantityType(PhysicalQuantityType):

    def __init__(self, sub_types: list[ApplicationAreaPhysicalQuantityType], **kwargs):
        super().__init__(**kwargs)
        self.sub_types = sub_types

    def check_args(self, namespace, package):
        ok = super().check_args(namespace, package)
        if not len(self.sub_types) > 1:
            namespace.WARNING(self.src, self.row_index,
                            f'{self.raw_name!r} should have at least two subtypes')

        return ok

    def create(self, namespace, package):
        if not self.check_args(namespace, package):
            return

        name = f'{self.raw_name}Unit'
        
        #print('---', name)
        abstract_data_type = namespace.ABSTRACT_DATA_TYPE(
            description=self.getdoc_for_nullable_type(),
            superTypes=[package.PhysicalQuantityUnit])
        setattr(package, name, abstract_data_type)

        for s_type in self.sub_types:
            s_type.create(namespace, package, [abstract_data_type])

    def getdoc_for_nullable_type(self):
        return f'''
            A unit of measurement for a physical quantity of type *{camel_to_normal(self.raw_name)}* with dimension
            {dimension_to_rst(self.physical_dim)}. <!SELF> has {len(self.sub_types)} subtypes for
            different application areas.'''

        
def read_uom_from_ods(src, namespace, package):
    for type_ in read_ods_uom_table(src, namespace):
        type_.create(namespace, package)

def read_ods_uom_table(src, namespace):
    
    quantity_types = []
    
    doc = ezodf.opendoc(src)
    sheet = doc.sheets[0]
    
    rows = [[item.value for item in ods_row] for ods_row in sheet if len(ods_row)]

    for row_index, row in enumerate(rows, 1):


        # row 1 and 2 contain labels of table
        if row_index < 3:
            continue

        # skip empty lines
        if set(row) == {None}:
            continue

        # for debugging
        #print(str(row_index), row)

        if row[0] is not None:
            raw_name = row[0]
            physical_dim = row[2]
            rdl_uri = row[3]
            comment = row[9]
            description = row[11]
            # reset lists for literals and subtypes
            uom_literals = []
            sub_types = []
            if rows[row_index][1] is None:
                # create simple type
                quantity_types.append(
                    SimplePhysicalQuantityType(
                        src=src,
                        row_index=row_index,
                        raw_name=raw_name,
                        physical_dim=physical_dim,
                        rdl_uri=rdl_uri,
                        uom_literals=uom_literals,
                        comment=comment,
                        description=description))
            else:
                # create application dependent type
                quantity_types.append(
                    ApplicationDependentPhysicalQuantityType(
                        src=src,
                        row_index=row_index,
                        raw_name=raw_name,
                        physical_dim=physical_dim,
                        rdl_uri=rdl_uri,
                        comment=comment,
                        sub_types=sub_types))

            continue

        if row[1] is not None:
            sub_type_name = row[1]
            rdl_uri = row[3]
            comment = row[9]
            application_area = row[10]
            description = row[11]
            # reset list for literals
            uom_literals = []
            # create application area type and update subtypes
            sub_type = ApplicationAreaPhysicalQuantityType(
                src=src,
                row_index=row_index,
                raw_name=sub_type_name,
                physical_dim=physical_dim,
                rdl_uri=rdl_uri,
                uom_literals=uom_literals,
                comment=comment,
                application_area=application_area,
                description=description,
                super_type_name=raw_name)
            sub_types.append(sub_type)

            continue

        # update uom literals
        uom_literals.append(
            UomLiteral(row_index, row[3], row[4], row[5], row[6], row[7], row[8], row[9]))

    return quantity_types
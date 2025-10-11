from collections import namedtuple
from pnb.mcl.utils import SYMBOL_PATTERN
import ezodf
import typing as T


EnumerationLiteral = namedtuple('EnumerationLiteral', ['row_index',
                                                       'literal',
                                                       'uri',
                                                       'label',
                                                       'symbol'])



class Enumeration:

    def __init__(self, src: str, row_index: int,
                 name: T.Any, literals: list[EnumerationLiteral]):
        self.src = src
        self.row_index = row_index
        self.name = name
        self.literals = literals
        
    def check_args(self, namespace, package):
        ok = True
        if not isinstance(self.name, str):
            ok = False
            namespace.ERROR(self.src, self.row_index,
                            f'{self.name!r} must be a string')
        elif not SYMBOL_PATTERN.fullmatch(self.name):
            ok = False
            namespace.ERROR(self.src, self.row_index,
                            f'{self.name!r} must have pattern of a symbol')
        elif not self.literals:
            namespace.WARNING(self.src, self.row_index,
                            f'{self.raw_name!r} has no literals')
        return ok

    def create(self, namespace, package):
        if not self.check_args(namespace, package):
            return
        
        enum = namespace.ENUMERATION(description=self.getdoc_for_enum())
        setattr(package, self.name, enum)
        
        for lit in self.literals:
            if not SYMBOL_PATTERN.fullmatch(lit.literal):
                #TODO: row index
                namespace.ERROR(self.src, 0,
                                f'{lit.literal!r} must have pattern of a symbol')
                continue
            setattr(enum, lit.literal, namespace.ENUMERATION_LITERAL(
                rdl_uri=lit.uri,
                rdl_label=lit.label,
                un_symbol=lit.symbol))

    def getdoc_for_enum(self):
        # TODO: doc
        return f'''
            '''



def read_enums_from_ods(src, namespace, package):
    for enum in read_ods_enums_table(src, namespace):
        enum.create(namespace, package)

def read_ods_enums_table(src, namespace):
    
    enums = []
    
    doc = ezodf.opendoc(src)
    sheet = doc.sheets[0]
    
    rows = [[item.value for item in ods_row] for ods_row in sheet if len(ods_row)]

    for row_index, row in enumerate(rows, 1):


        # row 1 contains labels of table
        if row_index < 2:
            continue

        # skip empty lines
        if set(row) == {None}:
            continue

        # for debugging
        #print(str(row_index), row)

        if row[0] is not None:
            name = row[0]
            # reset list for literals
            literals = []
            
            # create enumeration
            enums.append(
                Enumeration(
                    src=src,
                    row_index=row_index,
                    name=name,
                    literals=literals))

            continue

        # update enumeration literals
        literals.append(
            EnumerationLiteral(row_index, row[1], row[2], row[3], row[4]))

    return enums
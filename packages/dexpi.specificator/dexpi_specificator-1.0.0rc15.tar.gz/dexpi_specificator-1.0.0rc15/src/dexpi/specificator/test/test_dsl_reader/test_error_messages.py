import logging
import textwrap
import typing as T
import unittest

from lxml import etree
from pnb.mcl.io.xml import XmlExporter

from dexpi.specificator import dsl_reader

DEFAULT_LOGGING_LEVEL = logging.getLogger().level
TEST_LOGGING_LEVEL = logging.WARNING + 1

DEFAULT_DOCUMENTATION_URL = dsl_reader.DOCUMENTATION_URL
TEST_DOCUMENTATION_URL = 'https://www.test.org/'


class TestDslReader(unittest.TestCase):

    def assert_models(self,
            src: str,
            expected_model_xml_by_name: T.Optional[dict[str, str]]=None):
        self.assert_messages_and_models(src, '', expected_model_xml_by_name)

    def assert_messages_and_models(self,
            src: str,
            expected_messages: str,
            expected_model_xml_by_name: T.Optional[dict[str, str]]=None):

        assert logging.getLogger().level == DEFAULT_LOGGING_LEVEL
        logging.getLogger().setLevel(TEST_LOGGING_LEVEL)
        try:
            reader = dsl_reader.DslReader(textwrap.dedent(src).strip())
        finally:
            logging.getLogger().setLevel(DEFAULT_LOGGING_LEVEL)

        assert dsl_reader.DOCUMENTATION_URL == DEFAULT_DOCUMENTATION_URL
        dsl_reader.DOCUMENTATION_URL = TEST_DOCUMENTATION_URL
        try:
            actual_messages = '\n\n'.join(str(msg) for msg in reader.messages)
        finally:
            dsl_reader.DOCUMENTATION_URL = DEFAULT_DOCUMENTATION_URL

        expected_messages = textwrap.dedent(expected_messages).strip()

        test_report_lines = []

        if actual_messages != expected_messages:
            test_report_lines += [
                '',
                '',
                'actual_messages do not match expected_messages',
                '----------------------------------------------',
                '',
                'actual_messages:',
                '',
                actual_messages,
                '',
                'expected_messages:',
                '',
                expected_messages]

        built_model_by_name = dict(reader.model_by_name)
        del built_model_by_name['Builtin']

        expected_model_xml_by_name = expected_model_xml_by_name or {}

        names = set(built_model_by_name)
        names.update(expected_model_xml_by_name)

        for name in sorted(names):

            built_model = built_model_by_name.get(name)
            if built_model is None:
                test_report_lines += [
                    '',
                    '',
                    f'expected model "{name}" was not built',
                    '-------------------------------' + len(name)*'-']
                continue
            built_model_xml = etree.tostring(
                XmlExporter(built_model).xml,
                pretty_print=True,
                encoding='unicode').strip()

            expected_model_xml = expected_model_xml_by_name.get(name)
            if expected_model_xml is None:
                test_report_lines += [
                    '',
                    '',
                    f'unexpected model "{name}" was built',
                    '------------------------------' + len(name)*'-',
                    '',
                    built_model_xml]
                continue
            expected_model_xml = textwrap.dedent(expected_model_xml).strip()

            if expected_model_xml != built_model_xml:
                test_report_lines += [
                    '',
                    '',
                    f'XML for model "{name}" does not match expected XML',
                    '--------------------------------------------' + len(name)*'-',
                    '',
                    'actual XML:',
                    '',
                    built_model_xml,
                    '',
                    'expected XML:',
                    '',
                    expected_model_xml]

        if test_report_lines:
            self.fail('\n'.join(test_report_lines))


    def test_self_messages(self):
        with self.assertRaises(AssertionError) as ctx:
            self.assert_messages_and_models('', 'spam')
        self.assertEqual(
            str(ctx.exception).strip(),
            textwrap.dedent('''
                actual_messages do not match expected_messages
                ----------------------------------------------
                
                actual_messages:
                
                
                
                expected_messages:
                
                spam''').strip())


    def test_fatal_error(self):
        self.assert_messages_and_models('''
                Model = MODEL(name='Model', uri='http://www.example.org/Model')
                Model.Car = CONCRETE_CLASS()
                
                def calculate_upper_limit_for_color():
                    return 1 + 1 + 1/0
                
                Model.Car.Color = DATA_PROPERTY(
                    lower=0,
                    upper=calculate_upper_limit_for_color(),
                    type=BUILTIN.String)
            ''', '''
                #1 --- FATAL ERROR: fatal-error ---
                An error has occurred while reading the DSL source files:
                
                  Traceback (most recent call last):
                    File "<string>", line 9, in <module>
                    File "<string>", line 5, in calculate_upper_limit_for_color
                  ZeroDivisionError: division by zero
                
                This error prevents any further processing of the source files.
                (see https://www.test.org/fatal-error)
            ''')


    def test_missing_parameter_name(self):
        self.assert_messages_and_models('''
                MODEL()
            ''', '''
                #1 --- ERROR: missing-parameter ---
                - File "<string>", line 1
                  MODEL
                Parameter "name" is required, but missing.
                (see https://www.test.org/missing-parameter)
            ''')


    def test_invalid_parameter_type_name(self):
        self.assert_messages_and_models('''
                MODEL(name=1)
            ''', '''
                #1 --- ERROR: invalid-parameter-type ---
                - File "<string>", line 1
                  MODEL "1"
                Parameter "name": got 1 of type int, but value type must be one of str, NoneType.
                (see https://www.test.org/invalid-parameter-type)
            ''')


    def test_no_valid_identifier_as_parameter_spaces(self):
        self.assert_messages_and_models('''
                MODEL(name='spaces not allowed')
            ''', '''
                #1 --- ERROR: no-valid-identifier ---
                - File "<string>", line 1
                  MODEL "spaces not allowed"
                Parameter "name": 'spaces not allowed' is no valid value: An identifier must start with [a-zA_Z], followed by an arbitrary number of [a-zA_Z0-9_].
                (see https://www.test.org/no-valid-identifier)
            ''')


    def test_no_valid_identifier_as_parameter_leading_underscore(self):
        self.assert_messages_and_models('''
                TEMPLATE_MODEL(name='_LeadingUnderscoreNotAllowed')
            ''', '''
                #1 --- ERROR: no-valid-identifier ---
                - File "<string>", line 1
                  TEMPLATE_MODEL "_LeadingUnderscoreNotAllowed"
                Parameter "name": '_LeadingUnderscoreNotAllowed' is no valid value: An identifier must start with [a-zA_Z], followed by an arbitrary number of [a-zA_Z0-9_].
                (see https://www.test.org/no-valid-identifier)
            ''')

    # TODO   
    # def test_no_valid_identifier_as_parameter_leading_underscore_2(self):
    #     self.assert_messages_and_models('''
    #             Model = MODEL(name='Model', uri='http://www.example.org/Model')
    #             Model._A = CONCRETE_CLASS()
    #         ''', '''
    #             #1 --- ERROR: no-valid-identifier ---
    #             - File "<string>", line 1
    #               TEMPLATE_MODEL "_LeadingUnderscoreNotAllowed"
    #             Parameter "name": '_LeadingUnderscoreNotAllowed' is no valid value: An identifier must start with [a-zA_Z], followed by an arbitrary number of [a-zA_Z0-9_].
    #             (see https://www.test.org/no-valid-identifier)
    #         ''')


    def test_no_valid_identifier_by_assignment_umlaut(self):
        self.assert_messages_and_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.Päckchen = PACKAGE()
            ''', '''
                #1 --- ERROR: no-valid-identifier ---
                - File "<string>", line 2
                  PACKAGE "Päckchen"
                Parameter "name": 'Päckchen' is no valid value: An identifier must start with [a-zA_Z], followed by an arbitrary number of [a-zA_Z0-9_].
                (see https://www.test.org/no-valid-identifier)
            ''', dict(
                Model='<Model name="Model" uri="http://www.ex.org"/>'))

    # TODO
    # def test_name_invalid_Package_2(self):
    #     self.assert_messages_and_models('''
    #             Model1 = TEMPLATE_MODEL(name='Model1')
    #             Model1._Package1 = PACKAGE()
    #         ''', '''
    #         ''')

    def test_no_owner(self):
        self.assert_messages_and_models('''
                CONCRETE_CLASS()
            ''', '''
                #1 --- ERROR: no-owner ---
                - File "<string>", line 1
                  CONCRETE_CLASS
                The element is skipped because it is not assigned to any owner.
                (see https://www.test.org/no-owner)
            ''')

    def test_owner_skipped(self):
        self.assert_messages_and_models('''
                A_PACKAGE = PACKAGE()
                A_PACKAGE.A_SUB_PACKAGE = PACKAGE()
            ''', '''
                #1 --- ERROR: no-owner ---
                - File "<string>", line 1
                  PACKAGE
                The element is skipped because it is not assigned to any owner.
                (see https://www.test.org/no-owner)
                
                #2 --- ERROR: owner-skipped ---
                - File "<string>", line 2
                  PACKAGE "A_SUB_PACKAGE"
                causes: #1
                The element is skipped because its owner is skipped.
                (see https://www.test.org/owner-skipped)
            ''')

    def test_owner_skipped_model(self):
        self.assert_messages_and_models('''
                A_MODEL = MODEL()
                A_MODEL.A_PACKAGE = PACKAGE()
            ''', '''
                #1 --- ERROR: missing-parameter ---
                - File "<string>", line 1
                  MODEL
                Parameter "name" is required, but missing.
                (see https://www.test.org/missing-parameter)
                
                #2 --- ERROR: owner-skipped ---
                - File "<string>", line 2
                  PACKAGE "A_PACKAGE"
                causes: #1
                The element is skipped because its owner is skipped.
                (see https://www.test.org/owner-skipped)
            ''')

    def test_owner_skipped_anonymous(self):
        self.assert_messages_and_models('''
                A_MODEL = MODEL()
                A_MODEL.A_SUB_PACKAGE.A_PACKAGE = PACKAGE()
            ''', '''
                #1 --- ERROR: missing-parameter ---
                - File "<string>", line 1
                  MODEL
                Parameter "name" is required, but missing.
                (see https://www.test.org/missing-parameter)
                
                #2 --- ERROR: owner-skipped ---
                - File "<string>", line 2
                  reference to "A_SUB_PACKAGE"
                causes: #1
                The element is skipped because its owner is skipped.
                (see https://www.test.org/owner-skipped)
                
                #3 --- ERROR: owner-skipped ---
                - File "<string>", line 2
                  PACKAGE "A_PACKAGE"
                causes: #2
                The element is skipped because its owner is skipped.
                (see https://www.test.org/owner-skipped)
            ''')

    def test_missing_metatype(self):
        self.assert_messages_and_models('''
                A = MODEL(name='Model', uri='http://www.ex.org')
                A.B
            ''', '''
                #1 --- ERROR: missing-metatype ---
                - File "<string>", line 2
                  reference to "B"
                The element is skipped because no metatype is given.
                (see https://www.test.org/missing-metatype)
            ''', dict(
                Model='<Model name="Model" uri="http://www.ex.org"/>'))

    def test_missing_metatype_twice(self):
        self.assert_messages_and_models('''
                A = MODEL(name='Model', uri='http://www.ex.org')
                A.B
                A.B
            ''', '''
                #1 --- ERROR: missing-metatype ---
                - File "<string>", line 2
                  reference to "B"
                - File "<string>", line 3
                  reference to "B"
                The element is skipped because no metatype is given.
                (see https://www.test.org/missing-metatype)
            ''', dict(
                Model='<Model name="Model" uri="http://www.ex.org"/>'))

    def test_multiple_metatypes(self):
        self.assert_messages_and_models('''
                A = MODEL(name='Model', uri='http://www.ex.org')
                A.B = CONCRETE_CLASS()
                A.B
                A.B = ABSTRACT_CLASS()
            ''', '''
                #1 --- ERROR: multiple-metatypes ---
                - File "<string>", line 2
                  CONCRETE_CLASS "B"
                - File "<string>", line 4
                  ABSTRACT_CLASS "B"
                The element is skipped because multiple metatypes are given: AbstractClass, ConcreteClass.
                (see https://www.test.org/multiple-metatypes)
            ''', dict(
                Model='<Model name="Model" uri="http://www.ex.org"/>'))

    # TODO
    # def test_invalid_member_type(self):
    #     self.assert_messages_and_models('''
    #             A = MODEL(name='A', uri='http://www.ex.org/A')
    #             A.B = MODEL(name='B', uri='http://www.ex.org/B')
    #         ''', '''
    #             #1 --- ERROR: invalid-member-type ---
    #             - File "<string>", line 1
    #             - File "<string>", line 2
    #             Model A.B is skipped because Model A cannot have a member of this type.
    #             see file:///E:/s/w/p/specificator/doc/.build/html/dsl.html#invalid-member-type
    #         ''')

    def test_invalid_member_type(self):
        self.assert_messages_and_models('''
                A = MODEL(name='A', uri='http://www.ex.org')
                A.B = DATA_PROPERTY(lower=0, upper=1, type=BUILTIN.String)
            ''', '''
                #1 --- ERROR: invalid-member-type ---
                - File "<string>", line 2
                  DATA_PROPERTY "B"
                The element is skipped because its owner of type Model cannot have a member of type DataProperty.
                (see https://www.test.org/invalid-member-type)
            ''', dict(
                A='<Model name="A" uri="http://www.ex.org"/>'))

    def test_invalid_member_type_propagation(self):
        self.assert_messages_and_models('''
                A = MODEL(name='A', uri='http://www.ex.org')
                A.B = DATA_PROPERTY()
                A.B.C = DATA_PROPERTY()
            ''', '''
                #1 --- ERROR: invalid-member-type ---
                - File "<string>", line 2
                  DATA_PROPERTY "B"
                - File "<string>", line 3
                  reference to "B"
                The element is skipped because its owner of type Model cannot have a member of type DataProperty.
                (see https://www.test.org/invalid-member-type)
                
                #2 --- ERROR: owner-skipped ---
                - File "<string>", line 3
                  DATA_PROPERTY "C"
                causes: #1
                The element is skipped because its owner is skipped.
                (see https://www.test.org/owner-skipped)
            ''', dict(
                A='<Model name="A" uri="http://www.ex.org"/>'))

    def test_multiple_attribute_values(self):
        self.assert_messages_and_models('''
                A = MODEL(name='A', uri='http://www.ex.org')
                A.B = CONCRETE_CLASS()
                A.C = CONCRETE_CLASS(superTypes=[A.B])
                A.C = CONCRETE_CLASS(superTypes=[])
            ''', '''
                #1 --- ERROR: multiple-parameter-values ---
                - File "<string>", line 3
                  CONCRETE_CLASS "C"
                - File "<string>", line 4
                  CONCRETE_CLASS "C"
                The value for parameter "superTypes" is given several times. The parameter is ignored.
                (see https://www.test.org/multiple-parameter-values)
            ''', dict(A='''
                <Model name="A" uri="http://www.ex.org">
                  <ConcreteClass name="B"/>
                  <ConcreteClass name="C"/>
                </Model>'''))

    def test_cyclic_dependency_types(self):
        self.assert_messages_and_models('''
                A = MODEL(name='A', uri='http://www.ex.org')
                A.B = CONCRETE_CLASS(superTypes=[A.C])
                A.C = CONCRETE_CLASS(superTypes=[A.B])
            ''', '''
                #1 --- ERROR: cyclic-dependency ---
                - A.B
                  - File "<string>", line 2
                    CONCRETE_CLASS "B"
                  - File "<string>", line 3
                    reference to "B"
                - A.C
                  - File "<string>", line 2
                    reference to "C"
                  - File "<string>", line 3
                    CONCRETE_CLASS "C"
                Due to a cyclic dependency, these elements cannot be built.
                (see https://www.test.org/cyclic-dependency)
            ''', dict(
                A='<Model name="A" uri="http://www.ex.org"/>'))

    def test_templates_type_error(self):
        self.assert_messages_and_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.A = ABSTRACT_CLASS(templates=1)
            ''', '''
                #1 --- ERROR: invalid-parameter-type ---
                - File "<string>", line 2
                  ABSTRACT_CLASS "A"
                Parameter "templates": got 1 of type int, but value type must be list.
                (see https://www.test.org/invalid-parameter-type)
            ''', dict(
                Model='''
                    <Model name="Model" uri="http://www.ex.org">
                      <AbstractClass name="A"/>
                    </Model>'''))


    def test_templates_item_type_error(self):
        self.assert_messages_and_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.A = ABSTRACT_CLASS(templates=[1, 2])
            ''', '''
                #1 --- ERROR: invalid-parameter-type ---
                - File "<string>", line 2
                  ABSTRACT_CLASS "A"
                Parameter "templates[0]": got 1 of type int, but value type must be Property.
                (see https://www.test.org/invalid-parameter-type)
                
                #2 --- ERROR: invalid-parameter-type ---
                - File "<string>", line 2
                  ABSTRACT_CLASS "A"
                Parameter "templates[1]": got 2 of type int, but value type must be Property.
                (see https://www.test.org/invalid-parameter-type)
            ''', dict(
                Model='''
                    <Model name="Model" uri="http://www.ex.org">
                      <AbstractClass name="A"/>
                    </Model>'''))

    def test_skipped_element_used_templates(self):
        self.assert_messages_and_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.A = ABSTRACT_CLASS(templates=[Model.B])
            ''', '''
                #1 --- ERROR: missing-metatype ---
                - File "<string>", line 2
                  reference to "B"
                The element is skipped because no metatype is given.
                (see https://www.test.org/missing-metatype)
                
                #2 --- ERROR: skipped-element-used ---
                - File "<string>", line 2
                  ABSTRACT_CLASS "A"
                causes: #1
                Parameter "templates[0]": 'Model.B' is no valid value: It has been skipped.
                (see https://www.test.org/skipped-element-used)
            ''', dict(
                Model='''
                    <Model name="Model" uri="http://www.ex.org">
                      <AbstractClass name="A"/>
                    </Model>'''))


    def test_skipped_element_used_templates_2(self):
        self.assert_messages_and_models('''
                PROPERTY_TEMPLATES = TEMPLATE_MODEL(name='PropertyTemplates')
                PROPERTY_TEMPLATES.A = ABSTRACT_CLASS()
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.A = ABSTRACT_CLASS(templates=[PROPERTY_TEMPLATES.A])
            ''', '''
                #1 --- ERROR: invalid-member-type ---
                - File "<string>", line 2
                  ABSTRACT_CLASS "A"
                - File "<string>", line 4
                  reference to "A"
                The element is skipped because its owner of type TemplateModel cannot have a member of type AbstractClass.
                (see https://www.test.org/invalid-member-type)
                
                #2 --- ERROR: skipped-element-used ---
                - File "<string>", line 4
                  ABSTRACT_CLASS "A"
                causes: #1
                Parameter "templates[0]": 'PropertyTemplates.A' is no valid value: It has been skipped.
                (see https://www.test.org/skipped-element-used)
            ''', dict(
                Model='''
                    <Model name="Model" uri="http://www.ex.org">
                      <AbstractClass name="A"/>
                    </Model>'''))


    def test_empty(self):
        self.assert_models('', {})


    def test_abstract_class_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.A = ABSTRACT_CLASS()
            ''', dict(Model='''
                <Model name="Model" uri="http://www.ex.org">
                  <AbstractClass name="A"/>
                </Model>'''))


    def test_abstract_data_type_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.A = ABSTRACT_DATA_TYPE()
            ''', dict(Model='''
                <Model name="Model" uri="http://www.ex.org">
                  <AbstractDataType name="A"/>
                </Model>'''))


    def test_aggregated_data_type_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.A = AGGREGATED_DATA_TYPE()
            ''', dict(Model='''
                <Model name="Model" uri="http://www.ex.org">
                  <AggregatedDataType name="A"/>
                </Model>'''))


    def test_class_parameter_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.B = CONCRETE_CLASS()
                Model.A = CONCRETE_CLASS()
                Model.A.C = CLASS_PARAMETER(type=Model.B)
                Model.A.P = COMPOSITION_PROPERTY(lower=0, upper=3, type=Model.A.C)
            ''', dict(Model='''
                <Model name="Model" uri="http://www.ex.org">
                  <ConcreteClass name="A">
                    <ClassParameter name="C">
                      <ClassReference type="/B"/>
                    </ClassParameter>
                    <CompositionProperty name="P" isOrdered="false" lower="0" upper="3">
                      <ClassReference type="/A.C"/>
                    </CompositionProperty>
                  </ConcreteClass>
                  <ConcreteClass name="B"/>
                </Model>'''))


    def test_composition_property_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.example.org/Model')
                Model.Wheel = CONCRETE_CLASS()
                Model.Car = CONCRETE_CLASS()
                Model.Car.Wheels = COMPOSITION_PROPERTY(lower=0, upper=4, type=Model.Wheel)
            ''', dict(Model='''
                <Model name="Model" uri="http://www.example.org/Model">
                  <ConcreteClass name="Car">
                    <CompositionProperty name="Wheels" isOrdered="false" lower="0" upper="4">
                      <ClassReference type="/Wheel"/>
                    </CompositionProperty>
                  </ConcreteClass>
                  <ConcreteClass name="Wheel"/>
                </Model>'''))


    def test_concrete_class_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.A = CONCRETE_CLASS()
            ''', dict(Model='''
                <Model name="Model" uri="http://www.ex.org">
                  <ConcreteClass name="A"/>
                </Model>'''))


    def test_data_property_for_aggregated_data_type_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.example.org/Model')
                Model.WheelSpecification = AGGREGATED_DATA_TYPE()
                Model.WheelSpecification.Text = DATA_PROPERTY(lower=0, upper=1, type=BUILTIN.String)
            ''', dict(Model='''
                <Model name="Model" uri="http://www.example.org/Model">
                  <AggregatedDataType name="WheelSpecification">
                    <DataProperty name="Text" isOrdered="false" isUnique="false" lower="0" upper="1">
                      <DataTypeReference type="Builtin/String"/>
                    </DataProperty>
                  </AggregatedDataType>
                </Model>'''))


    def test_data_property_for_class_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.example.org/Model')
                Model.Car = CONCRETE_CLASS()
                Model.Car.Color = DATA_PROPERTY(lower=0, upper=1, type=BUILTIN.String)
            ''', dict(Model='''
                <Model name="Model" uri="http://www.example.org/Model">
                  <ConcreteClass name="Car">
                    <DataProperty name="Color" isOrdered="false" isUnique="false" lower="0" upper="1">
                      <DataTypeReference type="Builtin/String"/>
                    </DataProperty>
                  </ConcreteClass>
                </Model>'''))


    def test_data_type_parameter_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.A = AGGREGATED_DATA_TYPE()
                Model.A.P = DATA_PROPERTY(lower=0, upper=1, type=Model.A.C)
                Model.B = ABSTRACT_DATA_TYPE()
                Model.A.C = DATA_TYPE_PARAMETER(type=Model.B)
            ''', dict(Model='''
                <Model name="Model" uri="http://www.ex.org">
                  <AggregatedDataType name="A">
                    <DataTypeParameter name="C">
                      <DataTypeReference type="/B"/>
                    </DataTypeParameter>
                    <DataProperty name="P" isOrdered="false" isUnique="false" lower="0" upper="1">
                      <DataTypeReference type="/A.C"/>
                    </DataProperty>
                  </AggregatedDataType>
                  <AbstractDataType name="B"/>
                </Model>'''))


    def test_enumeration_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.A = ENUMERATION()
            ''', dict(Model='''
                <Model name="Model" uri="http://www.ex.org">
                  <Enumeration name="A"/>
                </Model>'''))


    def test_enumeration_literal_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.A = ENUMERATION()
                Model.A.B = ENUMERATION_LITERAL()
            ''', dict(Model='''
                <Model name="Model" uri="http://www.ex.org">
                  <Enumeration name="A">
                    <EnumerationLiteral name="B"/>
                  </Enumeration>
                </Model>'''))


    def test_model_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
            ''', dict(
                Model='<Model name="Model" uri="http://www.ex.org"/>'))


    def test_package_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.ex.org')
                Model.Package = PACKAGE()
            ''', dict(Model='''
                <Model name="Model" uri="http://www.ex.org">
                  <Package name="Package"/>
                </Model>'''))


    def test_reference_property_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.example.org/Model')
                Model.CarPort = CONCRETE_CLASS()
                Model.Car = CONCRETE_CLASS()
                Model.Car.LocatedIn = REFERENCE_PROPERTY(lower=0, upper=1, oppositeLower=0, oppositeUpper=1, type=Model.CarPort)
            ''', dict(Model='''
                <Model name="Model" uri="http://www.example.org/Model">
                  <ConcreteClass name="Car">
                    <ReferenceProperty name="LocatedIn" isOrdered="false" isUnique="false" lower="0" oppositeLower="0" oppositeUpper="1" upper="1">
                      <ClassReference type="/CarPort"/>
                    </ReferenceProperty>
                  </ConcreteClass>
                  <ConcreteClass name="CarPort"/>
                </Model>'''))


    def test_template_model_default(self):
        self.assert_models('''
                Model = MODEL(name='Model', uri='http://www.example.org/Model')
                TemplateModel = TEMPLATE_MODEL(name='TemplateModel', uri='http://www.example.org/TemplateModel')
                TemplateModel.P = DATA_PROPERTY(lower=0, upper=1, type=BUILTIN.String)
                Model.A = CONCRETE_CLASS(templates=[TemplateModel.P])
            ''', dict(Model='''
                <Model name="Model" uri="http://www.example.org/Model">
                  <ConcreteClass name="A">
                    <DataProperty name="P" isOrdered="false" isUnique="false" lower="0" upper="1">
                      <DataTypeReference type="Builtin/String"/>
                    </DataProperty>
                  </ConcreteClass>
                </Model>'''))

    
    
    


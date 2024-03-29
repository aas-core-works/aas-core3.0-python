# This code has been automatically generated by:
# dev_scripts/test_codegen/generate_test_for_descend_and_pass_through_visitor.py
# Do NOT edit or append.


"""
Test jointly :py:method:`aas_core3.types.Class.descend` and
:py:method:`aas_core3.types.PassThroughVisitor`.
"""


# pylint: disable=missing-docstring


from typing import (
    List,
    Sequence,
)
import unittest

import aas_core3.types as aas_types

import tests.common
import tests.common_jsonization


class _TracingVisitor(aas_types.PassThroughVisitor):
    """Visit the instances and trace them."""

    def __init__(self) -> None:
        """Initialize with an empty log."""
        self._log = []  # type: List[str]

    @property
    def log(self) -> Sequence[str]:
        """Get the tracing log."""
        return self._log

    def visit(self, that: aas_types.Class) -> None:
        self._log.append(tests.common.trace(that))
        super().visit(that)


def assert_tracing_logs_from_descend_and_visitor_are_the_same(
    that: aas_types.Class, test_case: unittest.TestCase
) -> None:
    """
    Check that the tracing logs are the same when :paramref:`that` instance
    is visited and when :paramref:`that` is ran through
    :py:method:`aas_types.Class.descend`.

    :param that: instance to be iterated over
    :param test_case: in which this assertion runs
    :raise: :py:class:`AssertionError` if the logs differ
    """
    log_from_descend = [tests.common.trace(something) for something in that.descend()]

    visitor = _TracingVisitor()
    visitor.visit(that)
    log_from_visitor = visitor.log

    test_case.assertGreater(len(log_from_visitor), 0)
    test_case.assertEqual(tests.common.trace(that), log_from_visitor[0])

    # noinspection PyTypeChecker
    test_case.assertListEqual(log_from_descend, log_from_visitor[1:])  # type: ignore


class Test_Extension(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_extension()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Extension"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_extension()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_AdministrativeInformation(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_administrative_information()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "AdministrativeInformation"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_administrative_information()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Qualifier(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_qualifier()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Qualifier"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_qualifier()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_AssetAdministrationShell(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_asset_administration_shell()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "AssetAdministrationShell"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_asset_administration_shell()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_AssetInformation(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_asset_information()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "AssetInformation"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_asset_information()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Resource(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_resource()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Resource"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_resource()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_SpecificAssetID(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_specific_asset_id()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "SpecificAssetId"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_specific_asset_id()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Submodel(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_submodel()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Submodel"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_submodel()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_RelationshipElement(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_relationship_element()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "RelationshipElement"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_relationship_element()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_SubmodelElementList(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_submodel_element_list()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "SubmodelElementList"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_submodel_element_list()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_SubmodelElementCollection(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_submodel_element_collection()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "SubmodelElementCollection"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_submodel_element_collection()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Property(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_property()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Property"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_property()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_MultiLanguageProperty(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_multi_language_property()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "MultiLanguageProperty"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_multi_language_property()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Range(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_range()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Range"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_range()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_ReferenceElement(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_reference_element()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "ReferenceElement"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_reference_element()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Blob(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_blob()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Blob"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_blob()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_File(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_file()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "File"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_file()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_AnnotatedRelationshipElement(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = (
            tests.common_jsonization.load_maximal_annotated_relationship_element()
        )
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "AnnotatedRelationshipElement"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = (
            tests.common_jsonization.load_maximal_annotated_relationship_element()
        )
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Entity(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_entity()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Entity"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_entity()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_EventPayload(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_event_payload()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "EventPayload"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_event_payload()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_BasicEventElement(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_basic_event_element()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "BasicEventElement"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_basic_event_element()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Operation(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_operation()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Operation"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_operation()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_OperationVariable(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_operation_variable()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "OperationVariable"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_operation_variable()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Capability(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_capability()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Capability"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_capability()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_ConceptDescription(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_concept_description()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "ConceptDescription"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_concept_description()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Reference(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_reference()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Reference"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_reference()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Key(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_key()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Key"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_key()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_LangStringNameType(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_lang_string_name_type()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "LangStringNameType"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_lang_string_name_type()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_LangStringTextType(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_lang_string_text_type()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "LangStringTextType"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_lang_string_text_type()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_Environment(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_environment()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "Environment"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_environment()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_EmbeddedDataSpecification(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_embedded_data_specification()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "EmbeddedDataSpecification"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_embedded_data_specification()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_LevelType(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_level_type()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "LevelType"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_level_type()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_ValueReferencePair(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_value_reference_pair()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "ValueReferencePair"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_value_reference_pair()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_ValueList(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_value_list()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "ValueList"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_value_list()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_LangStringPreferredNameTypeIEC61360(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = (
            tests.common_jsonization.load_maximal_lang_string_preferred_name_type_iec_61360()
        )
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "LangStringPreferredNameTypeIec61360"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = (
            tests.common_jsonization.load_maximal_lang_string_preferred_name_type_iec_61360()
        )
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_LangStringShortNameTypeIEC61360(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = (
            tests.common_jsonization.load_maximal_lang_string_short_name_type_iec_61360()
        )
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "LangStringShortNameTypeIec61360"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = (
            tests.common_jsonization.load_maximal_lang_string_short_name_type_iec_61360()
        )
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_LangStringDefinitionTypeIEC61360(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = (
            tests.common_jsonization.load_maximal_lang_string_definition_type_iec_61360()
        )
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "LangStringDefinitionTypeIec61360"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = (
            tests.common_jsonization.load_maximal_lang_string_definition_type_iec_61360()
        )
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


class Test_DataSpecificationIEC61360(unittest.TestCase):
    def test_descend_against_recorded_trace_log(self) -> None:
        instance = tests.common_jsonization.load_maximal_data_specification_iec_61360()
        expected_path = (
            tests.common.TEST_DATA_DIR
            / "descend_and_pass_through_visitor"
            / "DataSpecificationIec61360"
            / "maximal.json.trace"
        )

        log = [tests.common.trace(something) for something in instance.descend()]
        got_text = tests.common.trace_log_as_text_file_content(log)
        tests.common.record_or_check(expected_path, got_text)

    def test_descend_against_visitor(self) -> None:
        instance = tests.common_jsonization.load_maximal_data_specification_iec_61360()
        assert_tracing_logs_from_descend_and_visitor_are_the_same(instance, self)


if __name__ == "__main__":
    unittest.main()


# This code has been automatically generated by:
# dev_scripts/test_codegen/generate_test_for_descend_and_pass_through_visitor.py
# Do NOT edit or append.

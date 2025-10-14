# -*- coding: utf-8 -*-
import unittest
from rapidpro_api.validators import validate_field_name, validate_result_name, validate_lib_flow_name, validate_lib_group_name

# ignore pylint warnings
# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, invalid-name
class TestValidators(unittest.TestCase):

    #
    # Field Name Tests
    #
    def test_validate_field_name_empty(self):
        self.assertFalse(validate_field_name(""))

    def test_validate_field_name_valid(self):
        valid_names = ["field", "field-name", "a123", "valid-field-123"]
        for name in valid_names:
            with self.subTest(name=name):
                print(f"Testing field name: {name}")
                self.assertTrue(validate_field_name(name))

    def test_validate_field_name_too_long(self):
        too_long_name = "a" * 37
        self.assertFalse(validate_field_name(too_long_name))

    def test_validate_field_name_invalid_start(self):
        invalid_names = ["1field", "2-name", "9test"]
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validate_field_name(name))

    def test_validate_field_name_invalid_chars(self):
        invalid_names = ["field_name", "field@name", "field name", "field+name"]
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validate_field_name(name))

    #
    # Result Name Tests
    #
    def test_validate_result_name_empty(self):
        self.assertFalse(validate_result_name(""))

    def test_validate_result_name_valid(self):
        valid_names = ["result", "result-name", "result_name", "a123", "valid-result_123"]
        for name in valid_names:
            with self.subTest(name=name):
                self.assertTrue(validate_result_name(name))

    def test_validate_result_name_too_long(self):
        too_long_name = "a" * 65
        self.assertFalse(validate_result_name(too_long_name))

    def test_validate_result_name_invalid_start(self):
        invalid_names = ["1result", "2-name", "9test"]
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validate_result_name(name))

    def test_validate_result_name_invalid_chars(self):
        invalid_names = ["result@name", "result name", "result+name"]
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validate_result_name(name))

    #
    # Tests for lib flow names
    #
    def test_validate_lib_flow_name_empty(self):
        self.assertFalse(validate_lib_flow_name(""))

    def test_validate_lib_flow_name_valid(self):
        valid_names = ["flow", "flow-name", "flow_name", "a123", "valid-flow_123"]
        for name in valid_names:
            with self.subTest(name=name):
                self.assertTrue(validate_lib_flow_name(name))

    def test_validate_lib_flow_name_too_long(self):
        too_long_name = "a" * 65
        self.assertFalse(validate_lib_flow_name(too_long_name))

    def test_validate_lib_flow_name_invalid_start(self):
        invalid_names = ["1flow", "2-name", "9test"]
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validate_lib_flow_name(name))

    def test_validate_lib_flow_name_invalid_chars(self):
        invalid_names = ["flow@name", "flow name", "flow+name"]
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validate_lib_flow_name(name))

    #  Tests for lib group names
    def test_validate_lib_group_name_empty(self):
        self.assertFalse(validate_lib_group_name(""))

    def test_validate_lib_group_name_valid(self):
        valid_names = ["group", "group-name", "group_name", "a123", "valid-group_123"]
        for name in valid_names:
            with self.subTest(name=name):
                self.assertTrue(validate_lib_group_name(name))

    def test_validate_lib_group_name_too_long(self):
        too_long_name = "a" * 65
        self.assertFalse(validate_lib_group_name(too_long_name))

    def test_validate_lib_group_name_invalid_start(self):
        invalid_names = ["1group", "2-name", "9test"]
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validate_lib_group_name(name))

    def test_validate_lib_group_name_invalid_chars(self): 
        invalid_names = ["group@name", "group name", "group+name"]
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validate_lib_group_name(name))

    def test_validate_lib_group_name_invalid_chars(self):
        invalid_names = ["group@name", "group name", "group+name"]
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validate_lib_group_name(name))

    if __name__ == "__main__":
        unittest.main()

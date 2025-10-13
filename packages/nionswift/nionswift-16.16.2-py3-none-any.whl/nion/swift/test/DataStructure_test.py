# standard libraries
import contextlib
import copy
import math
import typing
import unittest

# third party libraries
import numpy

# local libraries
from nion.data import Calibration
from nion.data import DataAndMetadata
from nion.swift import Application
from nion.swift import Facade
from nion.swift.model import DataItem
from nion.swift.model import DataStructure
from nion.swift.model import Graphics
from nion.swift.model import Schema
from nion.swift.model import Symbolic
from nion.swift.model import Utility
from nion.swift.test import TestContext
from nion.ui import TestUI


Facade.initialize()


class TestDataStructureClass(unittest.TestCase):

    def setUp(self):
        TestContext.begin_leaks()
        self._test_setup = TestContext.TestSetup()

    def tearDown(self):
        self._test_setup = typing.cast(typing.Any, None)
        TestContext.end_leaks(self)

    def test_changing_entity_field_updates_data_structure(self):
        TestModel = Schema.entity("test_model", None, None, {"flag": Schema.prop(Schema.BOOLEAN)})
        with TestContext.create_memory_context() as test_context:
            DataStructure.DataStructure.register_entity(TestModel)
            try:
                document_model = test_context.create_document_model()
                data_structure = DataStructure.DataStructure(structure_type="test_model")
                document_model.append_data_structure(data_structure)
                self.assertIsNotNone(data_structure.entity)
                data_structure.entity._set_field_value("flag", False)
                self.assertEqual(data_structure.flag, False)
                self.assertEqual(data_structure.flag, data_structure.entity._get_field_value("flag"))
                data_structure.entity._set_field_value("flag", True)
                self.assertEqual(data_structure.flag, True)
                self.assertEqual(data_structure.flag, data_structure.entity._get_field_value("flag"))
            finally:
                DataStructure.DataStructure.unregister_entity(TestModel)

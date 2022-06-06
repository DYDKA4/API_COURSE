import unittest

import yaml

from app.parser.tosca_v_1_3.definitions.NotificationImplementationDefinition import \
    notification_implementation_definition_parser


class TestProperty(unittest.TestCase):
    # setUp method is overridden from the parent class TestCase
    def setUp(self):
        self.notification_implementation_definition_parser = notification_implementation_definition_parser

    # Each test method starts with the keyword test_
    def test_single_artifact(self):
        file = open('test_input/notification_implementation/single_artifact.yaml')
        data = file.read()
        file.close()
        data = yaml.safe_load(data)
        data = data.get('implementation')
        notification = notification_implementation_definition_parser(data)
        self.assertEqual(notification.vertex_type_system, 'NotificationImplementationDefinition')
        self.assertEqual(notification.primary_artifact_name, 'primary_artifact_test_name')

    def test_multiple_artifact(self): # todo make later with Artifact definition
        file = open('test_input/notification_implementation/single_artifact.yaml')
        data = file.read()
        file.close()
        data = yaml.safe_load(data)
        data = data.get('implementation')
import unittest
import click
from unittest.mock import patch
from lmctl.cli.commands.utils import Identifier, Identity, strip_identifiers, determine_identifier


class TestIdentifier(unittest.TestCase):

    def test_get_cli_display_name_uses_param_opts_if_set(self):
        identifier = Identifier(obj_attribute='personName', param_name='name', param_opts=['--name'])
        self.assertEqual(identifier.get_cli_display_name(), '--name')

    def test_get_cli_display_name_uses_param_name_if_opts_not_set(self):
        identifier = Identifier(obj_attribute='personName', param_name='name')
        self.assertEqual(identifier.get_cli_display_name(), 'name')

    def test_get_cli_display_name_fails_if_no_param_name_or_opts(self):
        identifier = Identifier(obj_attribute='personName')
        with self.assertRaises(TypeError) as ctx:
            identifier.get_cli_display_name()
        self.assertEqual(str(ctx.exception), 'Cannot retrieve cli_display_name for Identifier without "param_opts" or "param_name" (obj_attribute=personName)')

class TestUtils(unittest.TestCase):

    def test_strip_identifiers(self):
        param_args = {
            'unique_name': 'eNB-A', 
            'unique_slug': 'enb-a',
            'status': 'Active'
        }
        identifiers = [
            Identifier(obj_attribute='uniqueName', param_name='unique_name'),
            Identifier(obj_attribute='uniqueSlug', param_name='unique_slug', param_opts=['--id']),
            Identifier(obj_attribute='id')
        ]
        new_args = strip_identifiers(identifiers, **param_args)
        self.assertEqual(new_args, {'status': 'Active'})

    def test_determine_identifier_from_param(self):
        param_args = {
            'unique_name': 'eNB-A', 
        }
        identifiers = [
            Identifier(obj_attribute='uniqueName', param_name='unique_name'),
        ]
        file_content = {}
        result = determine_identifier(identifiers, 
                        file_content=file_content,
                        required=False,
                        **param_args)
        self.assertIsInstance(result, Identity)
        self.assertEqual(result.identifier, identifiers[0])
        self.assertEqual(result.value, 'eNB-A')
        self.assertFalse(result.from_file)
        self.assertTrue(result.from_params)

    def test_determine_identifier_from_file(self):
        param_args = {}
        identifiers = [
            Identifier(obj_attribute='uniqueName', param_name='unique_name'),
            Identifier(obj_attribute='uniqueSlug', param_name='unique_slug', param_opts=['--id']),
            Identifier(obj_attribute='id')
        ]
        file_content = {
            'uniqueName': 'eNB-A',
            'uniqueSlug': 'enb-a'
        }
        result = determine_identifier(identifiers, 
                        file_content=file_content,
                        required=False,
                        **param_args)
        self.assertIsInstance(result, Identity)
        self.assertEqual(result.identifier, identifiers[0])
        self.assertEqual(result.value, 'eNB-A')
        self.assertTrue(result.from_file)
        self.assertFalse(result.from_params)
    
    def test_determine_identifier_prioritises_param_over_file(self):
        param_args = {
            'unique_name': 'eNB-A'
        }
        identifiers = [
            Identifier(obj_attribute='uniqueName', param_name='unique_name'),
        ]
        file_content = {
            'uniqueName': 'eNB-B',
        }
        result = determine_identifier(identifiers, 
                        file_content=file_content,
                        required=False,
                        **param_args)
        self.assertIsInstance(result, Identity)
        self.assertEqual(result.identifier, identifiers[0])
        self.assertEqual(result.value, 'eNB-A')
        self.assertFalse(result.from_file)
        self.assertTrue(result.from_params)
    
    def test_determine_identifier_uses_first_param_found_in_order_of_identifiers(self):
        param_args = {
            'unique_slug': 'enb-a',
            'unique_name': 'eNB-A', 
            'status': 'Active'
        }
        identifiers = [
            Identifier(obj_attribute='uniqueName', param_name='unique_name'),
            Identifier(obj_attribute='uniqueSlug', param_name='unique_slug', param_opts=['--id']),
            Identifier(obj_attribute='id')
        ]
        file_content = {}
        result = determine_identifier(identifiers, 
                        file_content=file_content,
                        required=False,
                        **param_args)
        self.assertIsInstance(result, Identity)
        self.assertEqual(result.identifier, identifiers[0])
        self.assertEqual(result.value, 'eNB-A')
        self.assertFalse(result.from_file)
        self.assertTrue(result.from_params)

    def test_determine_identifier_uses_first_file_attr_found_in_order_of_identifiers(self):
        param_args = {}
        identifiers = [
            Identifier(obj_attribute='uniqueName', param_name='unique_name'),
            Identifier(obj_attribute='uniqueSlug', param_name='unique_slug', param_opts=['--id']),
            Identifier(obj_attribute='id')
        ]
        file_content = {
            'uniqueSlug': 'enb-a',
            'uniqueName': 'eNB-A',
        }
        result = determine_identifier(identifiers, 
                        file_content=file_content,
                        required=False,
                        **param_args)
        self.assertIsInstance(result, Identity)
        self.assertEqual(result.identifier, identifiers[0])
        self.assertEqual(result.value, 'eNB-A')
        self.assertTrue(result.from_file)
        self.assertFalse(result.from_params)

    def test_determine_identifiers_without_file_content(self):
        param_args = {
            'unique_name': 'eNB-A', 
        }
        identifiers = [
            Identifier(obj_attribute='uniqueName', param_name='unique_name'),
        ]
        result = determine_identifier(identifiers, 
                        file_content=None,
                        required=False,
                        **param_args)
        self.assertIsInstance(result, Identity)
        self.assertEqual(result.identifier, identifiers[0])
        self.assertEqual(result.value, 'eNB-A')
        self.assertFalse(result.from_file)
        self.assertTrue(result.from_params)

    def test_determine_identifiers_returns_none_if_not_required(self):
        param_args = {
            'serial': '123', 
        }
        identifiers = [
            Identifier(obj_attribute='uniqueName', param_name='unique_name'),
        ]
        file_content = {
            'status': 'Active'
        }
        result = determine_identifier(identifiers, 
                        file_content=file_content,
                        required=False,
                        **param_args)
        self.assertIsNone(result)

    @patch('lmctl.cli.commands.utils.identifier.click.get_current_context')
    def test_determine_identifiers_fails_if_required(self, mock_get_click_ctx):
        param_args = {
            'serial': '123', 
        }
        identifiers = [
            Identifier(obj_attribute='uniqueName', param_name='unique_name'),
        ]
        file_content = {
            'status': 'Active'
        }
        with self.assertRaises(click.UsageError) as ctx:
            determine_identifier(identifiers, 
                            file_content=file_content,
                            required=True,
                            **param_args)
        self.assertEqual(str(ctx.exception), 'Must identify the target by specifying the "unique_name" parameter or by including the "uniqueName" attribute in the given object/file')
    
    @patch('lmctl.cli.commands.utils.identifier.click.get_current_context')
    def test_determine_identifiers_fails_if_required_includes_param_in_msg(self, mock_get_click_ctx):
        param_args = {
            'serial': '123', 
        }
        identifiers = [
            Identifier(param_name='unique_name'),
        ]
        file_content = {
            'status': 'Active'
        }
        with self.assertRaises(click.UsageError) as ctx:
            determine_identifier(identifiers, 
                            file_content=file_content,
                            required=True,
                            **param_args)
        self.assertEqual(str(ctx.exception), 'Must identify the target by specifying the "unique_name" parameter')
    
    @patch('lmctl.cli.commands.utils.identifier.click.get_current_context')
    def test_determine_identifiers_fails_if_required_includes_includes_multiple_params_in_msg(self, mock_get_click_ctx):
        param_args = {
            'serial': '123', 
        }
        identifiers = [
            Identifier(param_name='unique_name'),
            Identifier(param_name='unique_slug'),
        ]
        file_content = {
            'status': 'Active'
        }
        with self.assertRaises(click.UsageError) as ctx:
            determine_identifier(identifiers, 
                            file_content=file_content,
                            required=True,
                            **param_args)
        self.assertEqual(str(ctx.exception), 'Must identify the target by specifying one parameter from ["unique_name", "unique_slug"]')
    
    @patch('lmctl.cli.commands.utils.identifier.click.get_current_context')
    def test_determine_identifiers_fails_if_required_uses_cli_display_name_in_msg(self, mock_get_click_ctx):
        param_args = {
            'serial': '123', 
        }
        identifiers = [
            Identifier(param_name='unique_name', param_opts=['-n', '--name']),
            Identifier(param_name='unique_slug', param_opts=['--slug']),
        ]
        file_content = {
            'status': 'Active'
        }
        with self.assertRaises(click.UsageError) as ctx:
            determine_identifier(identifiers, 
                            file_content=file_content,
                            required=True,
                            **param_args)
        self.assertEqual(str(ctx.exception), 'Must identify the target by specifying one parameter from ["-n, --name", "--slug"]')
    
    @patch('lmctl.cli.commands.utils.identifier.click.get_current_context')
    def test_determine_identifiers_fails_if_required_includes_obj_attr_in_msg(self, mock_get_click_ctx):
        param_args = {
            'serial': '123', 
        }
        identifiers = [
            Identifier(obj_attribute='uniqueName'),
        ]
        file_content = {
            'status': 'Active'
        }
        with self.assertRaises(click.UsageError) as ctx:
            determine_identifier(identifiers, 
                            file_content=file_content,
                            required=True,
                            **param_args)
        self.assertEqual(str(ctx.exception), 'Must identify the target by specifying or by including the "uniqueName" attribute in the given object/file')
    
    @patch('lmctl.cli.commands.utils.identifier.click.get_current_context')
    def test_determine_identifiers_fails_if_required_includes_all_obj_attr_in_msg(self, mock_get_click_ctx):
        param_args = {
            'serial': '123', 
        }
        identifiers = [
            Identifier(obj_attribute='uniqueName'),
            Identifier(obj_attribute='uniqueSlug'),
        ]
        file_content = {
            'status': 'Active'
        }
        with self.assertRaises(click.UsageError) as ctx:
            determine_identifier(identifiers, 
                            file_content=file_content,
                            required=True,
                            **param_args)
        self.assertEqual(str(ctx.exception), 'Must identify the target by specifying or by including one of the following attributes ["uniqueName", "uniqueSlug"] in the given object/file')
    
    @patch('lmctl.cli.commands.utils.identifier.click.get_current_context')
    def test_determine_identifiers_fails_if_required_includes_all_params_and_obj_attr_in_msg(self, mock_get_click_ctx):
        param_args = {
            'serial': '123', 
        }
        identifiers = [
            Identifier(obj_attribute='uniqueName', param_name='name'),
            Identifier(obj_attribute='uniqueSlug', param_name='slug', param_opts=['--slug']),
            Identifier(obj_attribute='id'),
            Identifier(param_name='ref', param_opts=['--ref']),
        ]
        file_content = {
            'status': 'Active'
        }
        with self.assertRaises(click.UsageError) as ctx:
            determine_identifier(identifiers, 
                            file_content=file_content,
                            required=True,
                            **param_args)
        self.assertEqual(str(ctx.exception), 'Must identify the target by specifying one parameter from ["name", "--slug", "--ref"] or by including one of the following attributes ["uniqueName", "uniqueSlug", "id"] in the given object/file')
    
    def test_determine_identifiers_treats_false_as_an_unset_param(self):
        param_args = {
            'latest': False, 
        }
        identifiers = [
            Identifier(param_name='latest')
        ]
        result = determine_identifier(identifiers, 
                            file_content=None,
                            required=False,
                            **param_args)
        self.assertIsNone(result)

        param_args['latest'] = True
        result = determine_identifier(identifiers, 
                            file_content=None,
                            required=False,
                            **param_args)
        self.assertIsNotNone(result)
        self.assertEqual(result.identifier, identifiers[0])

    def test_determine_identifiers_treats_false_as_an_unset_obj_attr(self):
        file_content = {
            'latest': False, 
        }
        identifiers = [
            Identifier(obj_attribute='latest')
        ]
        result = determine_identifier(identifiers, 
                            file_content=file_content,
                            required=False)
        self.assertIsNone(result)

        file_content['latest'] = True
        result = determine_identifier(identifiers, 
                            file_content=file_content,
                            required=False)
        self.assertIsNotNone(result)
        self.assertEqual(result.identifier, identifiers[0])
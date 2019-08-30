import unittest
from lmctl.reference import NotResolvableError, BadReferenceError
from lmctl.project.source.config_references import ConfigReferences
from lmctl.project.source.config import RootProjectConfig, SubprojectConfig, SubprojectEntry

class TestConfigReferences(unittest.TestCase):

    def test_resolve_root_descriptor_name(self):
        root = RootProjectConfig('2.0', 'root', '1.0', 'Assembly', None, [])
        references = ConfigReferences(root)
        result = references.resolve('$lmctl:/descriptor_name')
        self.assertEqual(result, 'assembly::root::1.0')

    def test_resolve_sub_descriptor_name(self):
        layer2_entry = SubprojectEntry('Layer2', 'Layer2', 'Resource', 'ansible-rm')
        layer1_entry = SubprojectEntry('Layer1', 'Layer1', 'Assembly', None, [layer2_entry])
        root = RootProjectConfig('2.0', 'root', '1.0', 'Assembly', None, [layer1_entry])
        references = ConfigReferences(root)
        result = references.resolve('$lmctl:/contains:/Layer1:/descriptor_name')
        self.assertEqual(result, 'assembly::Layer1-root::1.0')
        result = references.resolve('$lmctl:/contains:/Layer1:/contains:/Layer2:/descriptor_name')
        self.assertEqual(result, 'resource::Layer2-Layer1-root::1.0')

    def test_throws_not_resolvable_if_not_found(self):
        root = RootProjectConfig('2.0', 'root', '1.0', 'Assembly', None, [])
        references = ConfigReferences(root)
        with self.assertRaises(NotResolvableError) as context:
            references.resolve('$lmctl:/contains:/Layer1:/descriptor_name')
        self.assertEqual(str(context.exception), 'Cannot find \'Layer1\' in reference: $lmctl:/contains:/Layer1:/descriptor_name')

    def test_throws_bad_path_if_leads_to_non_dict(self):
        root = RootProjectConfig('2.0', 'root', '1.0', 'Assembly', None, [])
        references = ConfigReferences(root)
        with self.assertRaises(BadReferenceError) as context:
            references.resolve('$lmctl:/descriptor_name:/Layer1')
        self.assertEqual(str(context.exception), 'Reference has invalid step from \'descriptor_name\' to \'Layer1\': $lmctl:/descriptor_name:/Layer1')

    def test_invalid_reference(self):
        root = RootProjectConfig('2.0', 'root', '1.0', 'Assembly', None, [])
        references = ConfigReferences(root)
        with self.assertRaises(BadReferenceError) as context:
            references.resolve('$lc:/descriptor_name')
        self.assertEqual(str(context.exception), '\'$lc:/descriptor_name\' is not a valid reference')

    def test_build_descriptor_to_project_mapping_reference(self):
        root = RootProjectConfig('2.0', 'root', '1.0', 'Assembly', None, [])
        references = ConfigReferences(root)
        self.assertEqual(references.build_descriptor_to_project_mapping_reference('assembly::root::1.0'), '$lmctl:/descriptor_mappings:/assembly::root::1.0:/project')
        self.assertEqual(references.build_descriptor_to_project_mapping_reference('assembly::Layer1-root::1.0'), '$lmctl:/descriptor_mappings:/assembly::Layer1-root::1.0:/project')

    def test_build_descriptor_reference_root(self):
        root = RootProjectConfig('2.0', 'root', '1.0', 'Assembly', None, [])
        references = ConfigReferences(root)
        self.assertEqual(references.build_descriptor_reference(root), '$lmctl:/descriptor_name')

    def test_build_descriptor_reference_subprojects(self):
        layer2_entry = SubprojectEntry('Layer2', 'Layer2', 'Resource', 'ansible-rm')
        layer1_entry = SubprojectEntry('Layer1', 'Layer1', 'Assembly', None, [layer2_entry])
        root = RootProjectConfig('2.0', 'root', '1.0', 'Assembly', None, [layer1_entry])
        layer1_config = SubprojectConfig(root, layer1_entry)
        layer2_config = SubprojectConfig(layer1_config, layer2_entry)
        references = ConfigReferences(root)
        self.assertEqual(references.build_descriptor_reference(layer1_config), '$lmctl:/contains:/Layer1:/descriptor_name')
        self.assertEqual(references.build_descriptor_reference(layer2_config), '$lmctl:/contains:/Layer1:/contains:/Layer2:/descriptor_name')

import unittest
from tests.common.simulations.lm_simulator import SimulatedLm, NotFoundError

class TestSimulatedLm(unittest.TestCase):

    def test_add_descriptor(self):
        lm_sim = SimulatedLm()
        lm_sim.add_descriptor('name: assembly::test::1.0\ndescription: testing')
        project = lm_sim.get_project('assembly::test::1.0')
        self.assertEqual(project, {'id': 'assembly::test::1.0', 'name': 'assembly::test::1.0'})
        descriptor = lm_sim.get_descriptor('assembly::test::1.0')
        self.assertEqual(descriptor, 'name: assembly::test::1.0\ndescription: testing')

    def test_get_descriptor_throws_notfound(self):
        lm_sim = SimulatedLm()
        with self.assertRaises(NotFoundError) as context:
            lm_sim.get_descriptor('assembly::test::1.0')

    def test_delete_descriptor(self):
        lm_sim = SimulatedLm()
        lm_sim.add_descriptor('name: assembly::test::1.0\ndescription: testing')
        lm_sim.get_descriptor('assembly::test::1.0')
        lm_sim.delete_descriptor('assembly::test::1.0')
        with self.assertRaises(NotFoundError) as context:
            lm_sim.get_descriptor('assembly::test::1.0')

    def test_update_descriptor(self):
        lm_sim = SimulatedLm()
        lm_sim.add_descriptor('name: assembly::test::1.0\ndescription: testing')
        lm_sim.update_descriptor('name: assembly::test::1.0\ndescription: updated')
        descriptor = lm_sim.get_descriptor('assembly::test::1.0')
        self.assertEqual(descriptor, 'name: assembly::test::1.0\ndescription: updated')
        with self.assertRaises(NotFoundError) as context:
            lm_sim.update_descriptor('name: assembly::not-test::1.0')

    def test_add_project(self):
        lm_sim = SimulatedLm()
        lm_sim.add_project({'id': 'assembly::test::1.0', 'name': 'assembly::test::1.0'})
        project = lm_sim.get_project('assembly::test::1.0')
        self.assertEqual(project, {'id': 'assembly::test::1.0', 'name': 'assembly::test::1.0'})

    def test_get_project_throws_notfound(self):
        lm_sim = SimulatedLm()
        with self.assertRaises(NotFoundError) as context:
            lm_sim.get_project('assembly::test::1.0')

    def test_update_project(self):
        lm_sim = SimulatedLm()
        lm_sim.add_project({'id': 'assembly::test::1.0', 'name': 'assembly::test::1.0'})
        lm_sim.update_project({'id': 'assembly::test::1.0', 'name': 'assembly::test::1.0', 'description': 'updated'})
        project = lm_sim.get_project('assembly::test::1.0')
        self.assertEqual(project, {'id': 'assembly::test::1.0', 'name': 'assembly::test::1.0', 'description': 'updated'})
        with self.assertRaises(NotFoundError) as context:
            lm_sim.update_project({'id': 'assembly::not-test::1.0'})

    def test_add_assembly_configuration(self):
        lm_sim = SimulatedLm()
        lm_sim.add_project({'id': 'assembly::test::1.0', 'name': 'assembly::test::1.0'})
        lm_sim.add_assembly_configuration({'id': 'testconfig', 'projectId': 'assembly::test::1.0'})
        config = lm_sim.get_assembly_configuration('testconfig')
        self.assertEqual(config, {'id': 'testconfig', 'projectId': 'assembly::test::1.0'})
        configs_on_project = lm_sim.get_assembly_configurations_on_project('assembly::test::1.0')
        self.assertEqual(len(configs_on_project), 1)
        self.assertIn(config, configs_on_project)
        with self.assertRaises(NotFoundError) as context:
            lm_sim.add_assembly_configuration({'id': 'anotherconfg', 'projectId': 'assembly::not-test::1.0'})

    def test_get_assembly_configuration_throws_notfound(self):
        lm_sim = SimulatedLm()
        with self.assertRaises(NotFoundError) as context:
            lm_sim.get_assembly_configuration('test')

    def test_update_assembly_configuration(self):
        lm_sim = SimulatedLm()
        lm_sim.add_project({'id': 'assembly::test::1.0', 'name': 'assembly::test::1.0'})
        lm_sim.add_project({'id': 'assembly::test::2.0', 'name': 'assembly::test::2.0'})
        lm_sim.add_assembly_configuration({'id': 'testconfig', 'projectId': 'assembly::test::1.0'})
        lm_sim.update_assembly_configuration({'id': 'testconfig', 'projectId': 'assembly::test::2.0'})
        config = lm_sim.get_assembly_configuration('testconfig')
        self.assertEqual(config, {'id': 'testconfig', 'projectId': 'assembly::test::2.0'})
        configs_on_project1 = lm_sim.get_assembly_configurations_on_project('assembly::test::1.0')
        self.assertEqual(len(configs_on_project1), 0)
        configs_on_project2 = lm_sim.get_assembly_configurations_on_project('assembly::test::2.0')
        self.assertEqual(len(configs_on_project2), 1)
        self.assertIn(config, configs_on_project2)
        with self.assertRaises(NotFoundError) as context:
            lm_sim.update_assembly_configuration({'id': 'otherconfig'})

    def test_add_scenario(self):
        lm_sim = SimulatedLm()
        lm_sim.add_project({'id': 'assembly::test::1.0', 'name': 'assembly::test::1.0'})
        lm_sim.add_scenario({'id': 'testscenario', 'projectId': 'assembly::test::1.0'})
        scenario = lm_sim.get_scenario('testscenario')
        self.assertEqual(scenario, {'id': 'testscenario', 'projectId': 'assembly::test::1.0'})
        scenarios_on_project = lm_sim.get_scenarios_on_project('assembly::test::1.0')
        self.assertEqual(len(scenarios_on_project), 1)
        self.assertIn(scenario, scenarios_on_project)
        with self.assertRaises(NotFoundError) as context:
            lm_sim.add_scenario({'id': 'anotherscenario', 'projectId': 'assembly::not-test::1.0'})

    def test_get_scenario_throws_notfound(self):
        lm_sim = SimulatedLm()
        with self.assertRaises(NotFoundError) as context:
            lm_sim.get_scenario('test')

    def test_update_scenario(self):
        lm_sim = SimulatedLm()
        lm_sim.add_project({'id': 'assembly::test::1.0', 'name': 'assembly::test::1.0'})
        lm_sim.add_project({'id': 'assembly::test::2.0', 'name': 'assembly::test::2.0'})
        lm_sim.add_scenario({'id': 'testscenario', 'projectId': 'assembly::test::1.0'})
        lm_sim.update_scenario({'id': 'testscenario', 'projectId': 'assembly::test::2.0'})
        scenario = lm_sim.get_scenario('testscenario')
        self.assertEqual(scenario, {'id': 'testscenario', 'projectId': 'assembly::test::2.0'})
        scenarios_on_project1 = lm_sim.get_scenarios_on_project('assembly::test::1.0')
        self.assertEqual(len(scenarios_on_project1), 0)
        scenarios_on_project2 = lm_sim.get_scenarios_on_project('assembly::test::2.0')
        self.assertEqual(len(scenarios_on_project2), 1)
        self.assertIn(scenario, scenarios_on_project2)
        with self.assertRaises(NotFoundError) as context:
            lm_sim.update_scenario({'id': 'otherscenario'})

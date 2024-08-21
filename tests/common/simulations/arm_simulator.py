from unittest.mock import MagicMock
from lmctl.environment.armenv import ArmSession, ArmEnvironment
from lmctl.drivers.arm import AnsibleRmDriverException

class ArmSimulator:

    def __init__(self):
        pass

    def start(self):
        return SimulatedArm()

class SimulatedArm:

    def __init__(self):
        self.onboarded_types = {}
        self.mock = MagicMock()

    def onboard_type(self, resource_name, resource_version, resource_csar):
        self.onboarded_types[resource_name] = {'resource_version': resource_version, 'resource_csar': resource_csar}

    def as_mocked_session(self):
        return SimulatedArmSession(self)


class SimulatedArmSession(ArmSession):
    
    def __init__(self, arm_sim):
        self.env = ArmEnvironment(address='ArmSim', name='sim')
        self.sim = arm_sim
        self.__arm_driver = MagicMock()
        self.__arm_driver_sim = MockAnsibleRmDriver(self.sim)
        self.__configure_mocks()

    @property
    def arm_driver(self):
        return self.__arm_driver

    def __configure_mocks(self):
        self.__arm_driver.onboard_type.side_effect = self.__arm_driver_sim.onboard_type

class MockAnsibleRmDriver:

    def __init__(self, sim_arm):
        self.sim_arm = sim_arm

    def onboard_type(self, resource_name, resource_version, resource_csar):
        try:
            self.sim_arm.onboard_type(resource_name, resource_version, resource_csar)
        except Exception as e:
            raise AnsibleRmDriverException('Error: {0}'.format(str(e))) from e


# Targets
from .deployment_location import DeploymentLocations
from .resource_driver import ResourceDrivers
from .env import Environments
from .infrastructure_keys import InfrastructureKeys
from .behaviour_assembly_configurations import AssemblyConfigurations
from .behaviour_projects import Projects
from .behaviour_scenarios import Scenarios
from .behaviour_scenario_executions import ScenarioExecutions
from .descriptors import Descriptors
from .descriptor_templates import DescriptorTemplates
from .resource_managers import ResourceManagers
from .resource_packages import ResourcePackages
from .assemblies import Assemblies
from .clusters import Cluster
from .assembly_components import AssemblyComponents
from .resources import Resource
from .intents import Intents
from .processes import Processes
from .config import Configuration

target_instances = [
    DeploymentLocations(), 
    ResourceDrivers(), 
    Environments(), 
    InfrastructureKeys(), 
    AssemblyConfigurations(), 
    Projects(),
    Scenarios(),
    ScenarioExecutions(),
    Descriptors(),
    DescriptorTemplates(),
    ResourceManagers(),
    ResourcePackages(),
    Assemblies(),
    Cluster(),
    AssemblyComponents(),
    Resource(), 
    Intents(),
    Processes(),
    Configuration()
]
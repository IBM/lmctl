# Actions
from .get_action import Get
from .create_action import Create
from .update_action import Update
from .delete_action import Delete

actions = [Get, Create, Update, Delete]

# Targets
from .deployment_location import DeploymentLocation

targets = [DeploymentLocation()]

# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san SDK Software in commercial settings.
#
# END COPYRIGHT

from typing import Any
from typing import Dict
from typing import List

from logging import getLogger
from logging import Logger

from neuro_san.internals.interfaces.agent_network_validator import AgentNetworkValidator


class ToolboxNetworkValidator(AgentNetworkValidator):
    """
    Agent network validator for toolbox references.
    """

    def __init__(self, tools: Dict[str, Any]):
        """
        Constructor

        :param tools: A dictionary of tools, as read in from a toolbox_info.hocon file
        """
        self.logger: Logger = getLogger(self.__class__.__name__)
        self.tools: Dict[str, Any] = tools

    def validate(self, agent_network: Dict[str, Any]) -> List[str]:
        """
        Validate the agent network.

        :param agent_network: The agent network or name -> spec dictionary to validate
        :return: List of errors indicating agents and missing keywords
        """
        errors: List[str] = []

        self.logger.info("Validating toolbox agents...")

        if not agent_network:
            errors.append("Agent network is empty.")
            return errors

        # We can validate either from a top-level agent network,
        # or from the list of tools from the agent spec.
        name_to_spec: Dict[str, Any] = self.get_name_to_spec(agent_network)

        for agent_name, agent in name_to_spec.items():
            if agent.get("instructions") is None:  # This is a toolbox agent
                if self.tools is None or not isinstance(self.tools, Dict):
                    errors.append(f"Toolbox is unavailable. Cannot create Toolbox agent '{agent_name}'.")
                elif agent_name not in self.tools:
                    errors.append(f"Toolbox agent '{agent_name}' has no matching tool in toolbox.")

        return errors

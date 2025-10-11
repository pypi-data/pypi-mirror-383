from collections.abc import Callable
from typing import Any
from unittest.mock import Mock

from aiwebexplorer.agent_factory import get_agent
from aiwebexplorer.config import Environment, config
from aiwebexplorer.interfaces import IAgent


def get_agent_dep() -> Callable[..., IAgent[Any]]:
    """Get agent dependency based on environment configuration.

    Returns:
        Callable that returns either a real agent or a mock agent based on environment.
    """
    if config.ENV == Environment.CI:
        # Return a function that creates a mock agent for CI environment
        def mock_agent_factory(*args: Any, **kwargs: Any) -> IAgent[Any]:
            mock_agent = Mock(spec=IAgent[Any])
            return mock_agent

        return mock_agent_factory
    else:
        # Return the real get_agent function for all other environments
        return get_agent

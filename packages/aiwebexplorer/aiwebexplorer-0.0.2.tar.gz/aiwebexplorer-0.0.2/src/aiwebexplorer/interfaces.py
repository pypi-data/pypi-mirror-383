# === Interfaces ===
from typing import Protocol, TypeVar

# Type variable for response content
T = TypeVar("T")


class IResponse[T](Protocol):
    """Protocol for response objects with content property."""

    @property
    def content(self) -> T:
        """The content of the response."""
        ...


class IAgent[T](Protocol):
    """Protocol for agent objects that can run prompts asynchronously."""

    async def arun(self, prompt: str) -> IResponse[T]:
        """Run a prompt asynchronously and return a response.

        Args:
            prompt: The prompt to run

        Returns:
            A response object containing the result
        """
        ...


class AgentInterfaceError(Exception):
    """Exception for errors in the agent interface."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class BaseAgent:
    """
    Base class representing a generic agent in the Warlock ecosystem.
    To be implemented with specific agent behavior and MCP capabilities.
    """

    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name

    def execute_task(self, task_description: str) -> str:
        """
        Execute a given task. Stub implementation to be overridden.
        """
        raise NotImplementedError("Subclasses must implement execute_task")


from pydantic import BaseModel


class AgentTool:
    name: str = "tool"
    description: str = "this is tool"
    parameters: BaseModel = None

    @property
    def openai_model_dump(self) -> dict:
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters.model_json_schema() if self.parameters else {},
        }

from typing import Dict, Any

class ToolExcecute:

    def __init__(self):
        self.tools: Dict[str, Any] = {}

    def register_tool(self, name: str, description:str,  func: callable):
        if name in self.tools:
            raise ValueError(f"Tool with name '{name}' is already registered.")
        self.tools[name] ={"description": description, "func": func}
    
    def getTool(self,  name:str) -> callable:
        return self.tools.get(name, {}).get("func", None)

    def getAvailableTools(self) -> str:
        return "\n".join(
           [ f"- {name}: {info['description']}" for name, info in self.tools.items()]
        )

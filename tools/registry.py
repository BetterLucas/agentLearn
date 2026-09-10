

from typing import Any, Dict, Optional
from .base import Tool


class ToolRegistry():
    """
    工具注册表，用于管理和注册工具。
    """
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def registerTool(self, tool: Tool) -> None:
        """
        向工具箱中注册一个新工具。
        """
        if tool.name in self.tools:
            print(f"警告:工具 '{tool.name}' 已存在，将被覆盖。")
        self.tools[tool.name] = tool
        print(f"工具 '{tool.name}' 已注册。")

    # 别名，兼容 snake_case
    register_tool = registerTool

    def unregister(self, name: str) -> None:
        """
        从工具箱中注销一个工具。
        """
        if name in self.tools:
            del self.tools[name]
            print(f"工具 '{name}' 已注销。")
        else:
            print(f"警告:工具 '{name}' 不存在，无法注销。")


    def get_tool(self, name: str) -> Optional[Tool]:
        """
        根据名称获取一个工具实例。
        """
        return self.tools.get(name)


    def getToolFunc(self, name: str) -> Optional[callable]:
        """
        根据名称获取一个工具的执行函数。
        """
        tool = self.getTool(name)
        return tool.func if tool else None

    def list_tools(self) -> Dict[str, str]:
        """
        列出所有注册的工具及其描述。
        """
        return {name: tool.description for name, tool in self.tools.items()}

    def get_tools_description(self) -> str:
        """
        获取所有工具的描述信息。
        """
        if not self.tools:
            return "暂无可用工具"
        return "\n".join(
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        )

    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """
        执行指定名称的工具。
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        return tool.run(*args, **kwargs)


if __name__ == "__main__":
    # 测试工具注册表
    def sample_tool_function(x):
        return x * 2

    sample_tool = Tool(name="SampleTool", description="A sample tool that doubles the input.", func=sample_tool_function)

    registry = ToolRegistry()
    registry.registerTool(sample_tool)

    print(registry.list_tools())
    result = registry.execute_tool("SampleTool", 5)
    print(f"执行 SampleTool 的结果: {result}")
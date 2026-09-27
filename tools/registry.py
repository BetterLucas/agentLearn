
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from typing import Any, Callable, Dict, Optional
from tools.base import Tool




class ToolRegistry():
    """
    工具注册表，用于管理和注册工具。
    """
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.functions: Dict[str, Dict[str, Any]] = {}


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

    ## 兼容直接将函数注册为工具的方式
    def register_function_as_tool(self, func: Callable[[str],str], name: str, description: str) -> None:
        """
        将一个函数注册为工具。
        """
        if name in self.tools:
            print(f"警告:工具 '{name}' 已存在，将被覆盖。")

        self.functions[name] = {"description": description, 'func': func}
        print(f"函数 '{name}' 已注册为工具。")

    
    def unregister(self, name: str) -> None:
        """
        从工具箱中注销一个工具。
        """
        if name in self.tools:
            del self.tools[name]
            print(f"工具 '{name}' 已注销。")
        elif name in self.functions:
            del self.functions[name]
            print(f"函数 '{name}' 已从工具箱中注销。")
        else:
            print(f"警告:工具 '{name}' 不存在，无法注销。")


    def get_tool(self, name: str) -> Optional[Tool]:
        """
        根据名称获取一个工具实例。
        """
        return self.tools.get(name) or self.functions.get(name)

    def get_tool_description(self, name: str) -> Optional[str]:
        """
        根据名称获取一个工具的描述。
        """
        tool = self.get_tool(name)
        if tool:
            if isinstance(tool, Tool):
                return tool.description
            elif isinstance(tool, dict) and 'description' in tool:
                return tool['description']
        return None

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
        result = {}
        for name, tool in self.tools.items():
            result[name] = tool.description
        for name, func_info in self.functions.items():
            result[name] = func_info['description']
        return result

    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """
        执行指定名称的工具。
        """
        if name not in self.tools and name not in self.functions:
            raise ValueError(f"Tool '{name}' not found")

        ## 执行工具  兼容直接注册函数的方式
        if name in self.tools:
            tool = self.tools[name]
            return tool.run(*args, **kwargs)
        elif name in self.functions:
            tool = self.functions[name]['func']
            result = tool(*args, **kwargs)
            return result
        


if __name__ == "__main__":
    # 测试工具注册表
    def sample_tool_function(x):
        return x * 2

    registry = ToolRegistry()
    registry.register_function_as_tool(sample_tool_function, name="SampleTool", description="这是一个示例工具")

    print(registry.list_tools())
    result = registry.execute_tool("SampleTool", 5)
    print(f"执行结果: {result}")  # 输出: 执行结果: 10
  
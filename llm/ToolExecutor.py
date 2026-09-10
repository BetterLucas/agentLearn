
import inspect
from typing import Any, Dict
from tools import get_weather, get_attraction

class ToolExecutor:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: callable):
        """
        向工具箱中注册一个新工具。
        """
        if name in self.tools:
            print(f"警告:工具 '{name}' 已存在，将被覆盖。")
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")

    def getTool(self, name: str) -> callable:
        """
        根据名称获取一个工具的执行函数。
        """
        return self.tools.get(name, {}).get("func")

    def executeTool(self, name: str, tool_input: str) -> str:
        """
        根据函数签名自动拆分参数并调用工具。
        例如: get_attraction[成都,晴天] → get_attraction("成都", "晴天")
        """
        func = self.getTool(name)
        if not func:
            return f"错误:未找到名为 '{name}' 的工具。"

        # 获取函数参数名列表，如 ['city'] 或 ['city', 'weather']
        sig = inspect.signature(func)
        param_names = [p.name for p in sig.parameters.values()]

        # 按英文/中文逗号拆分输入
        input_parts = [p.strip() for p in tool_input.replace("，", ",").split(",")]

        # 参数数量不匹配时返回错误提示
        if len(input_parts) != len(param_names):
            return (
                f"错误:工具 '{name}' 需要 {len(param_names)} 个参数 "
                f"({', '.join(param_names)})，但收到了 {len(input_parts)} 个: "
                f"{tool_input}"
            )

        kwargs = dict(zip(param_names, input_parts))
        return func(**kwargs)

    def getAvailableTools(self) -> str:
        """
        获取所有可用工具的格式化描述字符串。
        """
        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])


if __name__== '__main__':
    executor = ToolExecutor()
    executor.registerTool("get_weather", "查询指定城市的实时天气。", get_weather)
    executor.registerTool("get_attraction", "根据城市和天气搜索推荐的旅游景点。", get_attraction)

    print("\n可用工具:")
    print(executor.getAvailableTools())

     # 4. 智能体的Action调用，这次我们问一个实时性的问题
    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "get_weather"
    tool_input = "成都"

    tool_function = executor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误:未找到名为 '{tool_name}' 的工具。")


from abc import abstractmethod
from typing import Any, Dict, List


class Tool():
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """执行工具的功能"""
        pass

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        """返回工具的参数信息"""
        pass

    def to_openai_schema(self) -> Dict[str, Any]:
        """
        将工具注册表转换为 OpenAI API 的工具描述格式。
        """
        tool_parameters = self.get_parameters()
        properties = {}
        required = []
        for para in tool_parameters:
            prop = {
                "type": para.type,
                "description": para.description
            }
            ## 如果有默认值，添加到描述中,openai schema不支持default字段
            if para.default_value is not None:
                prop["description"] = f"{para.description} (默认: {para.default})"

            # 如果是数组类型，添加 items 定义
            if para.type == "array":
                prop["items"] = {"type": "string"}  # 默认字符串数组

            properties[para.name] = prop
                    # 收集必需参数
            if para.required:
                required.append(para.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

class ToolParameter:
    def __init__(self, name: str, description: str, required: bool = True, default_value: Any = None):
        self.name = name
        self.description = description
        self.required = required
        

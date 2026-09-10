

from abc import abstractmethod
from typing import Any


class Tool():
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """执行工具的功能"""
        pass


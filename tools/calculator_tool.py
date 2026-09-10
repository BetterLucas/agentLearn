

from .base import Tool


class CalculatorTool(Tool):
    def __init__(self):
        super().__init__("calculator", "A tool for performing calculations.")

    def run(self, expression: str) -> str:
        try:
            # Strip potential "key=value" format from LLM-generated output (e.g. "expression=15*8+32")
            import re
            expr = re.sub(r'^[a-zA-Z_]\w*\s*=\s*', '', expression).strip()
            result = eval(expr, {"__builtins__": None}, {})
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"


import re
import sys
from pathlib import Path
from typing import List, Optional

# When running this script directly, add project root to sys.path
# Must be before any project-internal imports (tools, core, llm)
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.calculator_tool import CalculatorTool
from core.agent import Agent
from core.config import Config
from llm.LLMClient import HelloAgentsLLM
from tools.registry import ToolRegistry
from core.message import Message


MY_REACT_PROMPT = """你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤:

Thought: 分析当前问题，思考需要什么信息或采取什么行动。
Action: 选择一个行动，格式必须是以下之一:
- `{{tool_name}}[{{tool_input}}]` - 调用指定工具
- `Finish[最终答案]` - 当你有足够信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循:工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动:
"""



## 通过继承ReActAgent类，创建一个自定义的智能体类MyReactAgent
class ReactAgent(Agent):
    def __init__(
            self, 
            name: str,
            llm: HelloAgentsLLM,
            tool_registry: ToolRegistry,
            config: Optional[Config] = None,
            max_steps: int = 5,
            custom_prompt: Optional[str] = None
        ):
        super().__init__(name=name, llm=llm, system_prompt = custom_prompt, config=config)
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self.current_history: List[str] = []  # 用于存储当前对话的历史记录  
        self.prompt_template = custom_prompt if custom_prompt else MY_REACT_PROMPT
        print(f"✅ {name} 初始化完成，最大步数: {max_steps}")


    def run(self, question: str, **kwargs) -> str:
        self.current_history = []
        current_step = 0

        print(f"\n🤖 {self.name} 开始处理问题: {question}")

        while current_step <= self.max_steps:
            current_step += 1
            print(f"\n--- 第 {current_step} 步 ---")

            tools_desc = self.tool_registry.get_tools_description() ## 加载提示词描述
            history_str = "\n".join(self.current_history)
            prompt = self.prompt_template.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )

            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm.think(messages=messages, **kwargs)
            thought, action =  self._parse_output(response_text)
            if thought:
                print(f"🤔 思考: {thought}")

            if not action:
                print("⚠️ 警告: 未能解析出有效的Action，流程终止。")
                break

            if action.startswith("Finish"):
                final_answer = self._parse_action_input(action)
                self.add_message(Message(question, "user"))
                self.add_message(Message(final_answer, "assistant"))
                return final_answer

            
            tool_name, tool_input = self._parse_action(action)
            observation = self.tool_registry.execute_tool(tool_name, tool_input)
            print(f"🛠️ 执行工具: {tool_name}({tool_input}) -> 结果: {observation}")
            self.current_history.append(f"Action: {action}")
            self.current_history.append(f"Observation: {observation}")

        final_answer = "无法在规定步数内得出答案。"
        self.add_message(Message(question, "user"))
        self.add_message(Message(final_answer, "assistant"))
        return final_answer

    def _parse_output(self, text: str):
        """解析LLM的输出，提取Thought和Action。
        """
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # Action: 匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """解析Action字符串，提取工具名称和输入。
        """
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def _parse_action_input(self, action_text: str):
        """解析Finish动作，提取最终答案。
        """
        match = re.match(r"\w+\[(.*)\]", action_text)
        return match.group(1) if match else ""
        

if __name__ == "__main__":
    # 初始化LLM客户端和工具执行器
    
    toolregistry = ToolRegistry()
    # tool = Tool(name="get_weather", description="查询指定城市的实时天气。")
    calculator_tool = CalculatorTool()
    toolregistry.registerTool(tool=calculator_tool)
    
   
    # 创建ReAct智能体
    agent = ReactAgent(
        name="ReActAgent",
        llm=HelloAgentsLLM(),
        tool_registry=toolregistry,
        max_steps=5
    )

    # 测试问题
    user_question = "你好，帮我计算一下 1024*3+32 的结果。"
    agent.run(user_question)

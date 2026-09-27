
# 默认规划器提示词模板
from ast import Dict
import ast
from pathlib import Path
import sys
from typing import Optional
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.agent import Agent
from core.config import Config
from llm.LLMClient import HelloAgentsLLM


DEFAULT_PLANNER_PROMPT = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

# 默认执行器提示词模板
DEFAULT_EXECUTOR_PROMPT = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""

class Planner:
    """
    规划器类，用于生成任务的执行计划。
    """
    def __init__(self, llm_client: HelloAgentsLLM, prompt_template: Optional[str] = None):
        self.llm_client = llm_client
        self.prompt_template = prompt_template or DEFAULT_PLANNER_PROMPT

    def generate_plan(self, question: str) -> str:
        """
        根据任务描述生成执行计划。
        """
    
        prompt = self.prompt_template.format(question=question)
        messages = [{"role": "system", "content": prompt}]
        plan = self.llm_client.invoke(messages)

        print(f"📝 生成的计划: {plan} ")
        ## 解析计划，确保它是一个Python列表的字符串表示
        try:
            # 提取Python代码块中的列表
            plan_str = plan.split("```python")[1].split("```")[0].strip()
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 解析计划时出错: {e}")
            print(f"原始响应: {plan}")
            return []
        except Exception as e:
            print(f"❌ 解析计划时发生未知错误: {e}")
            return []

class Executor:
    "执行器类"

    def __init__(self, llm_client: HelloAgentsLLM, prompt_template: Optional[str] = None):
        self.llm_client = llm_client
        self.prompt_template = prompt_template or DEFAULT_EXECUTOR_PROMPT

    def execute_plan(self, question: str, plan: list) -> str:
        """
        执行整个计划，逐步解决问题。
        """
        history = []
        finnal_result = ""
        for i, step in enumerate(plan, 1):
            current_step = f"步骤 {i}: {step}"
            history_str = "\n".join([f"{h[0]} -> {h[1]}" for h in history])
            prompt = self.prompt_template.format(
                question=question,
                plan=plan,
                history=history_str,
                current_step=current_step
            )
            messages = [{"role": "user", "content": prompt}]
            result = self.llm_client.invoke(messages)
            history.append((current_step, result))
            print(f"✅ 执行结果: {current_step} -> {result}")
            finnal_result = result  # 更新最终结果为最后一步的结果
        return finnal_result




class PlanAndSolveAgent(Agent):
    """
    计划与执行智能体类。
    """
    def __init__(self, name: str, llm_client: HelloAgentsLLM, system_prompt: Optional[str] = None, config: Optional[Config] = None, custom_prompt: Optional[Dict[str, str]] = None):
        super().__init__(name=name, llm=llm_client, system_prompt=system_prompt, config=config)

        if custom_prompt is None:
            self.planner_prompt = DEFAULT_PLANNER_PROMPT
            self.executor_prompt = DEFAULT_EXECUTOR_PROMPT
        
        self.planner = Planner(llm_client)
        self.executor = Executor(llm_client)

    def run(self, question: str) -> str:
        """
        执行任务：先生成计划，再逐步执行。
        """
     
        print(f"🤖 {self.name} 开始处理问题: {question}")

        # 生成计划
        plan = self.planner.generate_plan(question)
        if not plan:
            print("❌ 未能生成有效的计划。")
            return "未能生成有效的计划。"

        print(f"📝 生成的计划: {plan}")

        # 执行计划
        final_result = self.executor.execute_plan(question, plan)
        print(f"🎯 最终结果: {final_result}")
        return final_result


if __name__ == "__main__":
   
    # 创建PlanAndSolveAgent
    llm_client = HelloAgentsLLM()
    agent = PlanAndSolveAgent(name="PlanAndSolveAgent", llm_client=llm_client)

    result = agent.run("一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？")
    print(f"最终结果: {result}")

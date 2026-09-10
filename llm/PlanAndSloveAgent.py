

from temp.Executor import Executor

from temp.Planner import Planner


class PlanAndSolveAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.planner = Planner(llm_client)
        self.executor = Executor(llm_client)



    def run(self, question: str):
        # Implement planning logic here
        print(f"\n--- 开始处理问题 ---\n问题: {question}")
        
        # 1. 调用规划器生成计划
        plan = self.planner.plan(question)
        
        # 检查计划是否成功生成
        if not plan:
            print("\n--- 任务终止 --- \n无法生成有效的行动计划。")
            return

        # 2. 调用执行器执行计划
        final_answer = self.executor.execute(question, plan)
        
        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")


if __name__ == "__main__":
    from temp.LLMClient import HelloAgentsLLM

    llm_client = HelloAgentsLLM()
    agent = PlanAndSolveAgent(llm_client)

    question = "我想计划一个为期一周的成都旅游行程，包括景点、美食和住宿。"
    agent.run(question)
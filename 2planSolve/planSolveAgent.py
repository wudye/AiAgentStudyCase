PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划,```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""
from agentFunc import HelloAgentsLLM
import ast
class Planner:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def plan(self, question: str) -> list[str]:
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        messages = [{"role": "user", "content": prompt}]

        print("Generating plan...")

        response_test = self.llm_client.think(messages)
        print(f"Plan response:\n{response_test}")
        try:
            plan_str = response_test.split("```python")[1].split("```")[0].strip()
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"Error parsing plan: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    


EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决“当前步骤”，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对“当前步骤”的回答:
"""


class Executor:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def execute(self, question: str, plan: list[str]) -> str:
        history = ""

        print("Executing plan...")

        for i, step in enumerate(plan):
            print(f"\n--- Executing Step {i+1}: {step} ---")
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else None,
                current_step=step
            )
            messages = [{"role": "user", "content": prompt}]
            response_test = self.llm_client.think(messages)
            history += f"Step {i+1}: {step}\nResult: {response_test}\n"
            print(f"Step {i+1} Result:\n{response_test}")

        final_answer = response_test
        return final_answer

class PlanSolveAgent:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
        self.planner = Planner(llm_client)
        self.executor = Executor(llm_client)

    def run(self, question: str) -> str:
        plan = self.planner.plan(question)
        if not plan:
            print("Failed to generate a valid plan.")
            return "Unable to generate a plan to solve the problem."


        final_answer = self.executor.execute(question, plan)


        return final_answer

if __name__ == "__main__":
    try: 
        llmClient = HelloAgentsLLM()
        agent = PlanSolveAgent(llmClient)
        question = "Explain the theory of relativity and its implications in modern physics."
        answer = agent.run(question)
        print(f"\nFinal Answer:\n{answer}")
    except Exception as e:
        print(f"Error initializing PlanSolveAgent: {e}")
PLANNER_PROMPT_TEMPLATE = """
You are a top-tier AI planning expert. Your task is to break down complex problems posed by users into an action plan consisting of multiple simple steps.
Ensure that each step in the plan is an independent, executable subtask, and strictly arranged in logical order.
Your output must be a Python list, where each element is a string describing a subtask.

Question: {question}

Please strictly output your plan in the following format, with ```python and ``` as necessary prefix and suffix:
```python
["Step 1", "Step 2", "Step 3", ...]
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
You are a top-tier AI execution expert. Your task is to solve problems step by step strictly according to the given plan.
You will receive the original question, the complete plan, and the steps and results completed so far.
Please focus on solving the "current step" and only output the final answer for that step, without any additional explanations or dialogue.
The output should be in English.

# Original Question:
{question}

# Complete Plan:
{plan}

# History of Steps and Results:
{history}

# Current Step:
{current_step}

Please only output the answer for the "current step":
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
from agentFunc import HelloAgentsLLM

from agentTool import ToolExcecute
from mcpfunc import search
import re

REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
- `Finish[最终答案]`:当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 Finish[最终答案] 来输出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""


class ReActAgent:
    def __init__(self, llm_clienr: HelloAgentsLLM,  tool_executor: ToolExcecute, max_steps: int=5):
        self.llm_client = llm_clienr
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question:str):
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- Step {current_step} ---")
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )

            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.think(messages)
            print(f"LLM Response:\n{response}")

            if not response:
                print("No response from LLM.")
                break
            thougt, action = self._parse_output(response)
            if thougt:
                print(f"Thought: {thougt}")
            if not action:
                print("No action found in LLM response.")
                break
            if action.startswith("Finish"):
                final_answer = re.match(r"Finish\[(.*)\]", action)
                print(f"Final Answer: {final_answer.group(1).strip() if final_answer else 'N/A'}")
                return final_answer
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                continue
            print(f"Executing Tool: {tool_name} with Input: {tool_input}")
            tool_func = self.tool_executor.getTool(tool_name)
            if not tool_func:
                observation = f"Tool '{tool_name}' not found."
            else:
                observation = tool_func(tool_input)
            print(f"Observation: {observation}")
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")



    def _parse_output(self,  text:str):
        thougt_match = re.search(r"Thought: (.*)", text)
        action_match = re.search(r"Action: (.*)", text)
        thougt = thougt_match.group(1).strip() if thougt_match else None
        action = action_match.group(1).strip() if action_match else None
        return thougt, action

    def _parse_action(self, action:str):
        match = re.match(r"(\w+)\[(.*)\]", action)
        if match:
            return match.group(1), match.group(2)
        return None, None

def main():
    toolExcecute = ToolExcecute()
    search_description="Use this tool to search the web for relevant information."
    toolExcecute.register_tool("Search", search_description, search)

    tool_name = "Search"
    tool_input = "the newest GPU model in 2026"

    tool_func = toolExcecute.getTool(tool_name)
    react_agent = ReActAgent(
        llm_clienr=HelloAgentsLLM(),
        tool_executor=toolExcecute
    )
    react_agent.run("the newest GPU model in 2026")

if __name__ == "__main__":
    main()
"""
智能对话助手 - 基于 LangGraph + Ollama 本地模型的对话系统
使用本地 Ollama 模型直接回答用户问题，无需外部 API
"""

import asyncio
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 定义状态结构
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    user_query: str        # 用户查询
    final_answer: str      # 最终答案
    step: str             # 当前步骤

# 初始化模型 - 使用 Ollama 本地模型
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID", "llama3.1:8b"),
    api_key=os.getenv("LLM_API_KEY", "ollama"),
    base_url=os.getenv("LLM_API_BASE_URL", "http://localhost:11434/v1"),
    temperature=0.7
)

def generate_answer_node(state: ChatState) -> ChatState:
    """直接使用本地模型回答用户问题"""
    
    # 获取最新的用户消息
    user_message = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break
    
    # 构建对话提示
    system_prompt = """你是一个智能助手，使用本地模型回答用户的问题。
请提供准确、有用的回答。如果是技术问题，请提供具体的解决方案或代码示例。
回答要结构清晰、易于理解。"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ])
    
    return {
        "final_answer": response.content,
        "step": "completed",
        "messages": [AIMessage(content=response.content)]
    }

# 构建对话工作流
def create_chat_assistant():
    workflow = StateGraph(ChatState)
    
    # 添加节点
    workflow.add_node("answer", generate_answer_node)
    
    # 设置线性流程
    workflow.add_edge(START, "answer")
    workflow.add_edge("answer", END)
    
    # 编译图
    memory = InMemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

async def main():
    """主函数：运行智能对话助手"""
    
    app = create_chat_assistant()
    
    print("💬 智能对话助手启动！")
    print(f"使用本地模型: {os.getenv('LLM_MODEL_ID', 'llama3.1:8b')}")
    print("支持各种问题：知识问答、技术问题、对话交流等")
    print("(输入 'quit' 退出)\n")
    
    session_count = 0
    
    while True:
        user_input = input("🤔 请输入您的问题: ").strip()
        
        if user_input.lower() in ['quit', 'q', '退出', 'exit']:
            print("感谢使用！再见！👋")
            break
        
        if not user_input:
            continue
        
        session_count += 1
        config = {"configurable": {"thread_id": f"chat-session-{session_count}"}}
        
        # 初始状态
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "final_answer": "",
            "step": "start"
        }
        
        try:
            print("\n" + "="*60)
            
            # 执行工作流
            async for output in app.astream(initial_state, config=config):
                for node_name, node_output in output.items():
                    if "messages" in node_output and node_output["messages"]:
                        latest_message = node_output["messages"][-1]
                        if isinstance(latest_message, AIMessage):
                            print(f"\n💡 回答:\n{latest_message.content}")
            
            print("\n" + "="*60 + "\n")
        
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            print("请重新输入您的问题。\n")

if __name__ == "__main__":
    asyncio.run(main())
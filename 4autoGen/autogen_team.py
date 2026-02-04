from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai._openai_client import ModelInfo
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.ui import Console
import traceback
import os
import asyncio
import dotenv
dotenv.load_dotenv()

def create_openai_client():
  
    model_name = os.getenv("LLM_MODEL_ID", "gpt-4")

    
    # For Ollama or non-OpenAI models, provide model_info with required 'family' field
    model_info = ModelInfo(
        family="llama",  # Required field for model family
        vision=False,
        function_calling=True,
        json_output=True
    )
    
    return OpenAIChatCompletionClient(
        model=model_name,
        api_key=os.getenv("LLM_API_KEY", "ollama"),
        base_url=os.getenv("LLM_API_BASE_URL", None),
        model_info=model_info
    )

def create_product_manager(model_client):
    sytem_message = """You are an experienced product manager specializing in requirements analysis
    and project planning for software products.
    your core responsibilities include:
    1. **Requirement Analysis**: Deeply understand user needs, identify core functionalities and 
    boundary conditions
    2. **Technical Planning**: Formulate clear techical implemetation paths based on requirements
    3. **Risk Management**: Identify potential technical risks and user experience issues
    4. **Coordination and Communication**: Effectively communicate with engineers and other team
    members

    When recieving a development task, please analyze it according to the following structure:
    1.Requirement understanding and analysis
    2.functional module division
    3.Technology selection recommendations
    4.Implementaion priority ranking
    5.Acceptance criteria definition

    please respond concisely and clearly, and say "Engineers please
    begin implementation" after comoleting the analysis."""

    return AssistantAgent(
        name="ProductManager",
        model_client=model_client,
        system_message=sytem_message
    )


def create_engineer(model_client):
    system_message = """You are a senior software engineer, skilled in Python development and
    web application building
    
    Your technical expertise includes:
    1: **Python Programming**: Proficient in Python syntax and best practices
    2. **Web Development**: Expert in frameworks such as Streamlit,  Flask, Django
    3. **API Integration**: Rich experience in third-party API integration
    4. **Error Handling**: Focus on code robustness and exception handling

    When receiving development tasks, please:
    1. Carefully analyze technical requirements
    2. Choose appropriate technical solutions
    3. Write complete code implementation
    4. Add necessary comments and explanations
    5. Consider edge cases and exception handling
    Please provide complete runnable code,  and say "Please code reviewer check" upon
    completion."""
    
    return AssistantAgent(
        name="Engineer",
        model_client=model_client,
        system_message=system_message
    )


def create_code_reviewer(model_client):
    system_message = """You are an experienced code review expert, focused on code quality and best practices.
    
    Your review priorites include:
    1. **Code Quality**: Check code readability, maintainability and performance
    2. **Security**: Identify potential security vulnerabilities and risk points
    3. **Best Practices**: Ensure code follows industry standards and best pratices
    4. **Error Handling**: Verify the completeness and reasonableness of exception handling

    Review process:
    1. Carefully read and understand code logic
    2. Check code standards and best practices
    3. Identify potential issuses and improvement points
    4. Provide specific modification suggestions
    5. Evaluate overall code quality

    Please provide specific review comments,  and say "Code review completed, please user agent test" 
    upon completion.

    """

    return AssistantAgent(
        name="CodeReviewer",
        model_client=model_client,
        system_message=system_message    
    )


def create_user_proxy():
    return UserProxyAgent(
        name="UserProxy",
        description="""User agent, responsible for the following duties:
        1. Represent users to propose development requirements
        2. Excecute the final code implementation
        3. Verify functionality meets expectations
        4. Provide user feedback and suggestions

        Please reply TERMINATE after completing testing."""
    )


async def run_software_development_team():

    print("------------1-------------initializing model client------------------")
    model_client = create_openai_client()
    print ("------------2-------------creating team------------------")
    product_manager = create_product_manager(model_client)
    engineer = create_engineer(model_client)
    code_reviewer = create_code_reviewer(model_client)
    user_proxy = create_user_proxy()

    termination = TextMentionTermination("TERMINATE")

    team_chat = RoundRobinGroupChat(
        participants=[product_manager, engineer, code_reviewer, user_proxy],
        termination_condition=termination,
        max_turns=20
    )

    task = """We need to develop a Bitcoin price display application with the following requirements:
    
    Core Features:
    - Display Bitcoin current price in real-time(USD)
    - Display 24-hour price change trend(percentage change and amount change)
    - Provide price refresh functionality

    Technical Requirements:
    - User Streamlit framework to create web application
    - Clean and beautiful interface,  User-friendly
    - Add appropriate error handling and loading states

    please collaborate as a team to complete this task,  from requirement analysis to final implementation.
    """
    print("------------3-------------starting team collaboration------------------")
    print('=' * 50)
    result = await Console(team_chat.run_stream(task=task))
    print("------------4-------------final result------------------")
    return result


if __name__ == "__main__":
    try:
        result = asyncio.run(run_software_development_team())
        print(f"\n collaboration result:")
        print(f"- working agents number: 4")
        print(f"- task status: {'success' if result else 'need improvement'}")

    except ValueError as e:
        print(f"Error: {e}")
        print("Please check the error message above and try again.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
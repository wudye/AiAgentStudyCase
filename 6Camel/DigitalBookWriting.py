from colorama import Fore
from camel.societies import RolePlaying
from camel.utils import print_text_animated
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from dotenv import load_dotenv
import os
import sys

# Set standard output encoding to UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")

# Create model using Ollama local model
model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI,
    model_type=LLM_MODEL,
    url=LLM_BASE_URL,
    api_key=LLM_API_KEY
)

# Define collaboration task
task_prompt = """
Create a short e-book about "The Psychology of Procrastination", targeting general readers interested in psychology.
Requirements:
1. Content should be scientifically rigorous, based on empirical research
2. Use accessible language, avoid excessive jargon
3. Include practical improvement suggestions and case studies
4. Length should be between 1000-2000 words
5. Clear structure including introduction, core chapters, and conclusion
6. All output must be in English
"""

print(Fore.YELLOW + f"Collaboration Task:\n{task_prompt}\n")

# Initialize role-playing session
role_play_session = RolePlaying(
    assistant_role_name="Psychologist",
    user_role_name="Writer",
    task_prompt=task_prompt,
    model=model
)

print(Fore.CYAN + f"Specific Task Description:\n{role_play_session.task_prompt}\n")

# Start collaborative dialogue
chat_turn_limit, n = 30, 0
input_msg = role_play_session.init_chat()

while n < chat_turn_limit:
    n += 1
    assistant_response, user_response = role_play_session.step(input_msg)
    
    print_text_animated(Fore.BLUE + f"Writer:\n\n{user_response.msg.content}\n")
    print_text_animated(Fore.GREEN + f"Psychologist:\n\n{assistant_response.msg.content}\n")

    # Check for task completion flag
    if "CAMEL_TASK_DONE" in user_response.msg.content:
        print(Fore.MAGENTA + "✅ E-book creation completed!")
        break
    
    input_msg = assistant_response.msg

print(Fore.YELLOW + f"Total collaborative dialogue turns: {n}")
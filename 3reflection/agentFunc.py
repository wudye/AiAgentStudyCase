import os
from dotenv import load_dotenv
from typing import List, Dict
from openai import OpenAI

load_dotenv()

from google import genai

# 1. Initialize the client (without the model name)
""" 
import google.generativeai as genai
genai.configure(api_key=self.apiKey, client_options={'timeout': self.timeout})
self.client = genai.GenerativeModel(self.model)
response = self.client.generate_content(
    "Your prompt here",
    request_options={"timeout": 600}  # Set your timeout here
)
print(response) """
class HelloAgentsLLM:
    def __init__(self, model: str=None, apiKey: str=None, timeout: int=None):
        self.model = model or os.getenv("LLM_MODEL_ID")
        self.apiKey = apiKey or os.getenv("LLM_API_KEY")
        self.timeout = 10  # default timeout in seconds
        if not all([self.model, self.apiKey]):
            raise ValueError("Model ID and API Key must be provided either as arguments or in environment variables.")
        if ":" in self.model or "llama" in self.model.lower():
            self.client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )
        else:
            self.client = genai.Client(
                api_key=self.apiKey 
                )

    def think(self, messages: List[Dict[str, str]], temperature: float=0) -> str:
        print(f" use the model:  {self.model} ")

        system_instruction = None
        user_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                system_instruction = msg['content']
            else:
                # 2. Convert OpenAI format {'content': '...'} to Google format {'parts': [{'text': '...'}]}
                user_messages.append({
                    "role": msg['role'],
                    "parts": [{"text": msg['content']}]
                })


        try:
            

        
            if ":" in self.model or "llama" in self.model.lower():
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    stream=True,
                    timeout=self.timeout
                )
                collected_content = []
                for chunk in response:
                    # OpenAI style delta checking
                    content = chunk.choices[0].delta.content or ""
                    print(content, end="", flush=True)
                    collected_content.append(content)
            
            else:
                response = self.client.models.generate_content_stream(
                model=self.model,
                contents=user_messages,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                    )
                ) 
                print("Response received from LLM.")
                collected_content = []
                for chunck in response:
                    content = chunck.text or ""
                    print(content, end="", flush=True)
                    collected_content.append(content)
            print()  
            return "".join(collected_content)
        except Exception as e:
            print(f"Error: {e}")
            return ""

if __name__ == "__main__":
    try: 
        llmClient = HelloAgentsLLM()

        example_messages = [
            {"role": "system",  "content": "You are a helpful assistant that writes python code."},
            {"role": "user",    "content": "Write a python function that prints 'Hello, World!'."}
        ]
        print("LLM Response:")
        responseText = llmClient.think(example_messages)
        if responseText:
            print(responseText)
    except Exception as e:
        print(f"Initialization Error: {e}")
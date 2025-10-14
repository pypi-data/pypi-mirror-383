import os 
import httpx 
from typing import Any, Dict, List, Optional
import inspect 
import time

api_base = os.getenv("MAESTRO_API_BASE", "http://localhost:8000/v1")

class ChatCompletions:
    """Chat """
    def __init__(self, api_key: str, api_base: str):
        self.api_key = api_key
        self.api_base = api_base
    
    def create(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        caller = inspect.stack()[1]
        start = time.perf_counter()
        payload = {"model": model, "messages": messages, "invocation_location": f"{caller.filename}/{caller.function}:{caller.lineno}", "start": start, **kwargs}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        with httpx.Client(timeout=300) as client:
            resp = client.post(f"{api_base}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            result = resp.json() 
            return result

class Chat:
    def __init__(self, api_key: str, api_base: str):
        self.completions = ChatCompletions(api_key, api_base)

class Responses:
    def __init__(self, api_key: str, api_base: str):
        self.api_key = api_key
        self.api_base = api_base

    def create(self, model: str, **kwargs) -> Dict[str, Any]:
        caller = inspect.stack()[1]
        start = time.perf_counter()
        payload = {"model": model, "invocation_location": f"{caller.filename}/{caller.function}:{caller.lineno}", "start": start, **kwargs}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        with httpx.Client(timeout=300) as client:
            resp = client.post(f"{api_base}/responses", json=payload, headers=headers)
            resp.raise_for_status()
            result = resp.json()
            return result 

class OpenAI:
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base or os.getenv("MAESTRO_API_BASE", "http://localhost:8000/v1")
        if not self.api_key:
            print("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.chat = Chat(self.api_key, self.api_base)
        self.responses = Responses(self.api_key, self.api_base)


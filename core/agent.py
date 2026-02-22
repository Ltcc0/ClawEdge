import json
import os
from openai import OpenAI
from config import settings

# Initialize the OpenAI client pointing to OpenRouter
# OpenRouter uses the standard OpenAI API format but a different base URL.
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENAI_API_KEY,
    # Optional: OpenRouter-specific headers for app identification
    default_headers={
        "HTTP-Referer": settings.BASE_URL or "https://agent-sentinel.local",
        "X-Title": "Agent Sentinel System",
    }
)

class AgentBrain:
    
    def analyze_and_plan(self, user_query: str) -> list[str]:
        """
        Phase 1: Monitor and Analyze using OpenRouter models.
        Instead of acting, the LLM breaks the request into subtasks.
        """
        system_prompt = (
            "You are a cautious AI Agent Supervisor. "
            "Do NOT execute the user's request directly. "
            "Instead, break the request down into a JSON list of logical subtasks "
            "that need to be performed. "
            "Output MUST be a raw JSON object with a key 'subtasks'. "
            "Example output: {\"subtasks\": [\"Search for AAPL stock price\", \"Calculate PE ratio\"]}"
        )

        try:
            # Using the model specified in env (e.g., 'deepseek/deepseek-chat' or 'anthropic/claude-3.5-sonnet')
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                # 'json_object' mode is supported by many OpenRouter models (like OpenAI/DeepSeek)
                # If using a model that doesn't support it, remove response_format and rely on prompt engineering.
                response_format={"type": "json_object"} 
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            # Robust parsing for various model outputs
            if "subtasks" in parsed:
                return parsed["subtasks"]
            if isinstance(parsed, list):
                return parsed
            
            return list(parsed.values())[0] if parsed else ["Analyze Request"]
            
        except Exception as e:
            print(f"LLM Planning Error: {e}")
            # Fallback for simple error handling
            return ["Error: Unable to generate plan via OpenRouter"]

    def execute_plan(self, plan: list[str]) -> str:
        """
        Phase 2: Execution.
        Simulates tool usage or acts as a orchestrator via OpenRouter.
        """
        system_prompt = "You are the Executor. Perform the following tasks and provide a concise final summary."
        plan_str = "\n".join(f"- {task}" for task in plan)
        
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Execute this plan:\n{plan_str}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Execution Error: {e}")
            return f"Error executing plan: {str(e)}"

agent_brain = AgentBrain()
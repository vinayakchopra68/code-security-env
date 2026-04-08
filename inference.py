# inference.py
import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- HACKATHON CHECKLIST COMPLIANCE ---
# 1. Defaults are set ONLY for API_BASE_URL and MODEL_NAME
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.cerebras.ai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.1-8b")
# 2. No default for HF_TOKEN
HF_TOKEN = os.getenv("HF_TOKEN") 

# 3. All LLM calls use the OpenAI client configured via these variables
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

# Replace with YOUR actual Hugging Face Space URL
ENV_URL = "https://vinayakchopra68-code-security-env.hf.space"

ACTION_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "review_action",
        "schema": {
            "type": "object",
            "properties": {
                "has_bug": {"type": "boolean"},
                "bug_category": {"type": "string", "enum": ["SQLi", "Auth", "Bounds", "None"]},
                "line_number": {"type": "integer"},
                "severity": {"type": "string", "enum": ["critical", "high", "medium", "low", "none"]},
                "explanation": {"type": "string"}
            },
            "required": ["has_bug", "bug_category", "line_number", "severity", "explanation"],
            "additionalProperties": False
        },
        "strict": True
    }
}

def run_agent_test(difficulty="hard"):
    # 4. Strict Stdout logs: START
    print(f"START | Difficulty: {difficulty}")
    
    response = requests.post(f"{ENV_URL}/reset?difficulty={difficulty}")
    observation = response.json()
    
    messages = [
        {"role": "system", "content": "You are a highly skilled cybersecurity auditor. Analyze the provided code snippet, find vulnerabilities, and output your findings in strict JSON format."}
    ]

    done = False
    step = 0

    while not done:
        step += 1
        # 4. Strict Stdout logs: STEP
        print(f"STEP | {step}")

        user_prompt = f"Code to review:\n{observation['code_snippet']}\n\nFeedback from grader: {observation['feedback']}"
        messages.append({"role": "user", "content": user_prompt})

        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            response_format=ACTION_SCHEMA,
            temperature=0.0
        )

        ai_response_json = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": ai_response_json})

        action_payload = json.loads(ai_response_json)
        step_response = requests.post(f"{ENV_URL}/step", json=action_payload)
        
        if step_response.status_code != 200:
            print(f"ERROR | Environment returned {step_response.status_code}")
            break

        step_result = step_response.json()
        observation = step_result["observation"]
        done = step_result["done"]
        reward = step_result["reward"]

    # 4. Strict Stdout logs: END
    print(f"END | Final Score: {reward}/1.0")

if __name__ == "__main__":
    run_agent_test("hard")
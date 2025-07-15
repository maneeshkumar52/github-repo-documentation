import os
import requests
import openai

class LLMClient:
    def __init__(self):
        self.backend = os.getenv("LLM_BACKEND", "ollama")  # "openai" or "ollama"
        self.model = os.getenv("LLM_MODEL", "llama3")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.openai_key = os.getenv("OPENAI_API_KEY")

    def complete(self, prompt, max_tokens=2048, temperature=0.2):
        if self.backend == "openai":
            openai.api_key = self.openai_key
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        else:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=300)
            response.raise_for_status()
            return response.json().get("response", "").strip()

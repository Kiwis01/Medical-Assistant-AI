# agents/base_agent.py
from llm.gemini import GeminiLLM

class BaseAgent:
    def __init__(self, config):
        self.config = config
        self.logger = config.logger
        self.llm = GeminiLLM(config)
        self.tools = None

    def handle_query(self, query):
        raise NotImplementedError("Each agent must implement its own handle_query method.")
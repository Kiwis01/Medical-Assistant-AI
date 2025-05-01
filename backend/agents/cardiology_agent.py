# agents/cardiology_agent.py
import os
from agents.base_agent import BaseAgent
from utils.imports import *
from agent_tools.cardiology_agent_tools import CardiologyAgentTools
from utils.common_utils import *

class CardiologyAgent(BaseAgent):
    def handle_query(self, query):
        # Use GeminiLLM or other logic
        self.logger.info(f"@cardiology_agent.py Handling query")
        self.tools = CardiologyAgentTools(self.config)
        
        # Get instructions from config
        instructions = self.config.cardiology_instructions
        instructions_text = "\n".join(instructions)

        # Filter only user messages
        user_messages = [msg for msg in query if msg.get("role") == "user"]

        # Get relevant research for the query
        latest_query = query
        for msg in reversed(latest_query):
            if msg.get("role") == "user":
                latest_query = msg.get("text", "")
                break

        # Clean up the query to remove file paths
        cleaned_query = latest_query
        if contains_image_file(latest_query):
            # If the query is just a file path, use a generic cardiology term instead
            cleaned_query = "cardiac symptoms"
            self.logger.info(f"@cardiology_agent.py Cleaned query for research: {cleaned_query}")

        # Get relevant research
        research_context = ""
        if cleaned_query:
            research_context = self.tools.get_relevant_research(cleaned_query)
       
        # Generate prompt
        prompt = (
            f"You are a cardiology specialist. "
            f"Instructions:\n{instructions_text}\n\n"
            f"Research Context:\n{research_context}\n\n"
            f"Patient symptoms: {query}\n"
            f"Based on the above, provide your medical reasoning and recommendation."
        )
        # Generate response using the LLM with the cardiology specialty context
        response = self.llm.generate(prompt)
        self.logger.info("@cardiology_agent.py Generated response")
        return response
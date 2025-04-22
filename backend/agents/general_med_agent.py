# agents/general_med_agent.py
from agents.base_agent import BaseAgent

class GeneralMedAgent(BaseAgent):
    def handle_query(self, query):
        # Use GeminiLLM or other logic
        self.logger.info(f"@general_med_agent.py Handling query")
        
        # Get instructions from config
        instructions = self.config.generalmedicine_instructions
        instructions_text = "\n".join(instructions)
        
        # Generate prompt
        prompt = (
            f"You are a general medicine specialist. "
            f"Instructions:\n{instructions_text}\n\n"
            f"Patient symptoms: {query}\n"
            f"Based on the above, provide your medical reasoning and recommendation."
        )
        # Generate response using the LLM with the general medicine specialty context
        response = self.llm.generate(prompt)
        return response

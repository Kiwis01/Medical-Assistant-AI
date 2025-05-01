# agents/cardiology_agent.py
from agents.base_agent import BaseAgent

class CardiologyAgent(BaseAgent):
    def handle_query(self, query):
        # Use GeminiLLM or other logic
        self.logger.info(f"@cardiology_agent.py Handling query")
        
        # Get instructions from config
        instructions = self.config.cardiology_instructions
        instructions_text = "\n".join(instructions)

        # Generate prompt
        prompt = (
            f"You are a cardiology specialist. "
            f"Instructions:\n{instructions_text}\n\n"
            f"Patient symptoms: {query}\n"
            f"Based on the above, provide your medical reasoning and recommendation."
        )
        # Generate response using the LLM with the cardiology specialty context
        response = self.llm.generate(prompt)
        return response
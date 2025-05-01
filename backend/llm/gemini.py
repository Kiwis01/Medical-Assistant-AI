import google.generativeai as genai

class GeminiLLM:
    def __init__(self, config):
        self.api_key = config.gemini_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        self.conversation = [] # store conversation history
        self.specialty_dict = config.specialty_dict
        
    def generate(self,conversation_history: list) -> str:
        response = self.model.generate_content(
            contents=conversation_history,
            generation_config={
                "temperature": 1.0,
                "max_output_tokens": 200,
                "top_p": 0.9,
                "top_k": 10,
            },
        )
        return response.text.strip()
    
    def predict_specialty(self, symptoms: str) -> str:
        system_instruction = (
            "\n".join(self.specialty_dict) +
            f"Symptoms: {symptoms}\n" +
            "Specialty: \n"
        )
        response = self.model.generate_content(
            system_instruction,
            generation_config={
                "temperature": 0.5,
                "max_output_tokens": 20,
                "top_p": 0.9,
                "top_k": 10,
            },
        )
        return response.text.strip()


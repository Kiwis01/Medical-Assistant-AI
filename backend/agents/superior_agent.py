from utils.imports import *
from llm.gemini import GeminiLLM
from agents.neurology_agent import NeurologyAgent
from agents.cardiology_agent import CardiologyAgent
from agents.general_med_agent import GeneralMedAgent

class SuperiorAgent:
    def __init__(self, config):
        self.api_key = config.gemini_key
        self.logger = config.logger
        self.specialist_agents = {
            "Cardiology": CardiologyAgent(config),
            "Neurology": NeurologyAgent(config),
            # "Orthopedics": OrthopedicsAgent(config),
            # "Dermatology": DermatologyAgent(config),
            "General Medicine": GeneralMedAgent(config)
            # "Pediatrics": PediatricsAgent(config)
        }
        #initialize gemini
        self.llm = GeminiLLM(config)
        
    def determine_specialty(self, symptoms: str) -> str:
        try:
            specialty = self.llm.predict_specialty(symptoms)
            # Ensure the specialty is one of our defined specialties
            if specialty in self.specialist_agents.keys():
                self.logger.info(f"@superior_agent.py Determined specialty: {specialty}")
                return specialty
            else:
                self.logger.warning(f"@superior_agent.py Could not determine a specialty")
                return specialty
        except (KeyError, IndexError, Exception) as e:
            self.logger.error(f"@superior_agent.py Error {str(e)}")
            return specialty
from utils.imports import *
import os 

class Config:
    def __init__(self, path='config/config.json'):
        
        log_path = os.path.join(os.path.dirname(__file__), "app.log")
        self.logger = logging.getLogger("medrag_logger")
        self.logger.setLevel(logging.INFO)

        # Prevent adding handlers multiple times in case of re-imports
        if not self.logger.handlers:
            # File handler
            file_handler = logging.FileHandler(log_path, mode='a')
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(console_handler)

        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            data = {}
        

        self.gemini_key = data.get("GEMINI_KEY", "")
        self.secret_key = data.get("SECRET_KEY", "")
        self.qdrant_key = data.get("QDRANT_KEY", "")
        self.neurology_instructions = data.get("neurology_instructions", [])
        self.cardiology_instructions = data.get("cardiology_instructions", [])
        self.dermatology_instructions = data.get("dermatology_instructions", [])
        self.oncology_instructions = data.get("oncology_instructions", [])
        self.generalmedicine_instructions = data.get("generalmedicine_instructions", [])
        self.pediatrics_instructions = data.get("pediatrics_instructions", [])
        self.image_output_dir = data.get("image_output_dir", "")
        self.image_input_dir = data.get("image_input_dir", "")
        self.specialty_dict = data.get("specialty_dict", [])
        self.image_tracking = {}
        
        self.google_api_key = data.get("google_api_key", "")
        self.google_cse_id = data.get("google_cse_id", "")
        self.search_engine_key = data.get("search_engine_key", "")

        self.logger.info("@config.py initialized successfully")


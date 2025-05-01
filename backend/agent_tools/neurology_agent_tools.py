import os
import requests
import cv2
from flask import current_app
from agent_tools.research_tools import ResearchTools

class NeurologyAgentTools:
    def __init__(self, config):
        self.logger = config.logger
        self.research = ResearchTools(config)

    
    def get_relevant_research(self, query, condition=None):
        """Get relevant research for a query"""
        search_query = query
        if condition:
            search_query = f"{query} {condition}"
            
        # Add neurology-specific terms to improve search
        enhanced_query = f"neurology {search_query} brain"
        
        results = self.research.search_medical_literature(
            enhanced_query, 
            specialty="Neurology",
            limit=3
        )
        
        return self.research.format_research_for_prompt(results)

    def get_prediction(self, image_path: str):
        url = "https://medai-api-f34085d124bb.herokuapp.com/uploadfile/"
        try:
            
            # Important: Keep the file open within the same block where you use it
            with open(image_path, "rb") as file:
                files = {"file": file}
                response = requests.post(url, files=files)
                
            # Process response after file is closed
            if response.ok:
                prediction = response.json()['prediction']['predictions']
                return prediction
            else:
                self.logger.error(f"@neurology_agent_tools.py API error: {response.status_code} - {response.text}")
                return f"Error from prediction API: {response.status_code}"
                
        except Exception as e:
            self.logger.error(f"@neurology_agent_tools.py Error getting image: {str(e)}")
            return f"Error processing image: {str(e)}"

    def draw_box(self, predictions, filepath):
        try:
            # Load the image
            image = cv2.imread(filepath)
            if image is None:
                self.logger.error(f"@neurology_agent_tools.py Could not read image: {filepath}")
                return None, os.path.basename(filepath)
            
            # Draw boxes for each prediction
            for pred in predictions:
                # Extract coordinates and dimensions using your original formula
                x = int(pred.get('x', 0))
                y = int(pred.get('y', 0))
                w = int(pred.get('width', 0))
                h = int(pred.get('height', 0))
            
                # Convert center (x, y) to top-left (x1, y1) and bottom-right (x2, y2)
                x1 = int(x - w / 2)
                y1 = int(y - h / 2)
                x2 = int(x + w / 2)
                y2 = int(y + h / 2)
                
                confidence = pred.get('confidence', 0)
                class_name = pred.get('class', 'unknown')
                
                # Draw rectangle
                color = (0, 255, 0)  # Green for tumor
                thickness = 2
                cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
                
                # Add label
                label = f"{class_name}: {confidence:.2f}"
                cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, thickness)

            
            # Save the annotated image
            file_name = f"annotated_{os.path.basename(filepath)}"
            save_path = os.path.join(current_app.config['GENERATED_FOLDER'], file_name)
            cv2.imwrite(save_path, image)
            
            self.logger.info(f"@neurology_agent_tools.py Generated image: {file_name}")
            return image, file_name
            
        except Exception as e:
            self.logger.error(f"@neurology_agent_tools.py Error drawing boxes: {str(e)}")
            return None, os.path.basename(filepath)
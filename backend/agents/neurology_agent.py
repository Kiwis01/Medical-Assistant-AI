# agents/neurology_agent.py
import os
from agents.base_agent import BaseAgent
from utils.imports import *
from agent_tools.neurology_agent_tools import NeurologyAgentTools
from utils.common_utils import *


class NeurologyAgent(BaseAgent):
    def handle_query(self, query):
        # Use GeminiLLM or other logic
        self.logger.info(f"@neurology_agent.py Handling query")
        self.tools = NeurologyAgentTools(self.config)
        
        # Get instructions from config
        instructions_text = "\n".join(self.config.neurology_instructions)

        # Filter only user messages
        user_messages = [msg for msg in query if msg.get("role") == "user"]

        # prediction variables
        image_path = None
        prediction_response = None

        # find image path in the last 5 messages
        for message in user_messages[-5:]:
            text = message.get("text", "")
            extracted_path = contains_image_file(text)
            if extracted_path:
                image_path = os.path.basename(extracted_path)
                self.logger.info(f"@neurology_agent.py Found image '{image_path}' in conversation")

        # if the image path is found, get prediction
        if image_path is not None:
            image_path = f"{current_app.config['UPLOAD_FOLDER']}/{image_path}"
            # Check if this image has already been processed
            self.logger.info(f"@neurology_agent.py Image file exists: {image_path}")
            if is_image_tracked(image_path):
                # Use cached prediction
                prediction_response = get_image_prediction(image_path)
                self.logger.info(f"@neurology_agent.py Using cached prediction for {image_path}")
            else:
                # Generate new prediction
                prediction_response = self.tools.get_prediction(image_path)
                self.logger.info(f"@neurology_agent.py {prediction_response}")
                self.logger.info(f"@neurology_agent.py Got prediction")
                
                # Track the prediction
                add_tracked_image(image_path, prediction_response, self.logger)
        
        # generate image with bounding boxes
        if prediction_response is not None:
            # Check if we already generated an image for this
            if has_generated_image(image_path):
                # Use cached generated image path
                generated_image_path = get_generated_image_path(image_path)
                self.logger.info(f"@neurology_agent.py Using cached generated image: {generated_image_path}")
            else:
                # Generate new image with bounding boxes
                image, file_name = self.tools.draw_box(prediction_response, image_path)
                
                # Track the generated image
                add_generated_image(image_path, file_name, self.logger)

                # --- Add bot image message to conversation history ---
                rel_generated_path = f"/generated/{file_name}"
                conversation_history = query  # assuming 'query' is the history list
                conversation_history.append({"role": "model", "text": rel_generated_path})

        # Get relevant research for the query
        latest_query = query
        for msg in reversed(latest_query):
            if msg.get("role") == "user":
                latest_query = msg.get("text", "")
                break

        # Clean up the query to remove file paths
        cleaned_query = latest_query
        if contains_image_file(latest_query):
            # If the query is just a file path, use condition or a generic term instead
            condition = None
            if prediction_response and isinstance(prediction_response, list) and len(prediction_response) > 0:
                condition = prediction_response[0].get('class')
                cleaned_query = f"symptoms of {condition}" if condition else "neurological symptoms"
            else:
                cleaned_query = "neurological symptoms"
            self.logger.info(f"@neurology_agent.py Cleaned query for research: {cleaned_query}")

        # Get relevant research
        research_context = ""
        if cleaned_query:
            # Detect if there's a specific condition mentioned
            condition = None
            if prediction_response and isinstance(prediction_response, list) and len(prediction_response) > 0:
                # Extract condition from prediction if available
                condition = prediction_response[0].get('class')    
            research_context = self.tools.get_relevant_research(cleaned_query, condition)
       
        # Generate prompt
        prompt = (
            f"You are a neurology specialist. "
            f"Instructions:\n{instructions_text}\n\n"
            f"Research Context:\n{research_context}\n\n"
            f"Tumor prediction response if available: {prediction_response}\n\n"
            f"Patient symptoms: {query}\n"
            f"Based on the above, provide your medical reasoning and recommendation."
        )
        # Generate response using the LLM with the neurology specialty context
        response = self.llm.generate(prompt)
        self.logger.info("@neurology_agent.py Generated response")
        return response
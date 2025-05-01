import os
import requests
from flask import current_app
from agent_tools.research_tools import ResearchTools

class CardiologyAgentTools:
    def __init__(self, config):
        self.logger = config.logger
        self.research = ResearchTools(config)
    
    def get_relevant_research(self, query, condition=None):
        """Get relevant cardiology research for a query"""
        search_query = query
        if condition:
            search_query = f"{query} {condition}"
            
        # Add cardiology-specific terms to improve search
        enhanced_query = f"cardiology {search_query} heart"
        
        results = self.research.search_medical_literature(
            enhanced_query, 
            specialty="Cardiology",
            limit=3
        )
        
        return self.research.format_research_for_prompt(results)

from tenacity import retry, stop_after_attempt, wait_random_exponential
from utils.imports import *

class ResearchTools:
    def __init__(self, config):
        self.config = config
        self.logger = config.logger
        self.cache = {}  # Simple in-memory cache
    
    def search_medical_literature(self, query, specialty=None, limit=5):
        """Search for medical literature using multiple sources"""
        self.logger.info(f"@research_tools.py Searching for: {query}")
        
        # Create a cache key
        cache_key = f"{query}_{specialty}_{limit}"
        
        # Check cache first
        if cache_key in self.cache:
            self.logger.info("Using cached research results")
            return self.cache[cache_key]
        
        # Try PubMed first
        pubmed_results = self.search_pubmed(query, specialty, limit=limit)
        
        # If PubMed returns enough results, use those
        if len(pubmed_results) >= limit:
            self.cache[cache_key] = pubmed_results
            return pubmed_results
            
        # Log that we're trying Google as fallback
        self.logger.info(f"PubMed returned only {len(pubmed_results)} results, trying Google search")

        # Otherwise, supplement with Google results
        google_results = self.search_google_medical(
            query, 
            limit=limit - len(pubmed_results)
        )

        # Log Google results
        self.logger.info(f"Google search returned {len(google_results)} results")
        
        # Combine results
        combined_results = pubmed_results + google_results
        # If still no results, return a fallback
        if not combined_results:
            fallback = [{
                "title": "Medical Information Notice",
                "content": "No specific medical literature was found for this query. The following response is based on general medical knowledge. Please consult with a healthcare professional for personalized medical advice.",
                "source": "MedRAG System Notice"
            }]
            self.logger.info("Using fallback medical information notice")
            self.cache[cache_key] = fallback
            return fallback
        
        # If still no results, return a fallback
        if not combined_results:
            fallback = [{
                "title": "Medical Information Notice",
                "content": "No specific medical literature was found for this query. Please consult with a healthcare professional for personalized medical advice.",
                "source": "MedRAG System Notice"
            }]
            self.cache[cache_key] = fallback
            return fallback
        
        self.cache[cache_key] = combined_results
        return combined_results
    
    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def search_pubmed(self, query, specialty=None, limit=5):
        """Search PubMed for relevant medical literature"""
        self.logger.info(f"@research_tools.py Searching PubMed for: {query}")
        
        # Enhance query with specialty if provided
        search_term = query
        if specialty:
            search_term = f"{query} {specialty}"
        
        # Extract key medical terms and simplify query
        # This helps PubMed find more relevant results
        simplified_terms = self._extract_medical_terms(search_term)
        if simplified_terms:
            search_term = simplified_terms
        
        self.logger.info(f"Simplified PubMed search term: {search_term}")
            
        try:
            # Step 1: Search for article IDs
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
            search_url = f"{base_url}esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": search_term,
                "retmode": "json",
                "retmax": limit
            }
            
            search_response = requests.get(search_url, params=search_params)
            search_data = search_response.json()
            
            # Extract article IDs
            article_ids = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not article_ids:
                self.logger.info("No PubMed results found")
                return []
                
            # Step 2: Fetch article details
            summary_url = f"{base_url}esummary.fcgi"
            summary_params = {
                "db": "pubmed",
                "id": ",".join(article_ids),
                "retmode": "json"
            }
            
            summary_response = requests.get(summary_url, params=summary_params)
            summary_data = summary_response.json()
            
            # Process results
            results = []
            for article_id in article_ids:
                article = summary_data.get("result", {}).get(article_id, {})
                
                if article:
                    title = article.get("title", "Untitled Article")
                    abstract = article.get("abstract", "No abstract available")
                    authors = article.get("authors", [])
                    author_names = [author.get("name", "") for author in authors if author.get("name")]
                    author_string = ", ".join(author_names[:3])
                    if len(author_names) > 3:
                        author_string += " et al."
                    
                    journal = article.get("fulljournalname", "Medical Journal")
                    pub_date = article.get("pubdate", "")
                    
                    results.append({
                        "title": title,
                        "content": abstract,
                        "authors": author_string,
                        "journal": journal,
                        "date": pub_date,
                        "source": f"PubMed ID: {article_id}",
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{article_id}/"
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching PubMed: {str(e)}")
            return []

    def _extract_medical_terms(self, query):
        """Extract key medical terms from a natural language query"""

        # Check if query contains a file path and skip it
        if query.startswith('/') and ('.' in query.split('/')[-1]):
            self.logger.info("Query appears to be a file path, skipping term extraction")
            return None

        # Comprehensive list of medical terms to extract
        common_symptoms = [
            # General symptoms
            "headache", "pain", "fever", "nausea", "dizzy", "dizziness", 
            "fatigue", "tired", "weakness", "numbness", "swelling", "inflammation",
            
            # Neurological terms
            "tumor", "cancer", "seizure", "migraine", "stroke", "tremor",
            "memory loss", "confusion", "glioma", "meningioma", "neuroma",
            "brain", "head", "skull", "cranial", "neural", "nerve", "spinal",
            
            # Cardiovascular terms
            "heart", "chest pain", "palpitation", "hypertension", "arrhythmia",
            
            # Respiratory terms
            "cough", "shortness of breath", "wheezing", "asthma", "pneumonia",
            
            # Gastrointestinal terms
            "abdominal pain", "nausea", "vomiting", "diarrhea", "constipation"
        ]
        
        # Extract individual words and phrases
        words = query.lower().split()
        medical_terms = [word for word in words if word in common_symptoms]
        
        # Also check for multi-word terms
        for term in common_symptoms:
            if ' ' in term and term.lower() in query.lower():
                medical_terms.append(term)
        
        if medical_terms:
            # Remove duplicates while preserving order
            unique_terms = []
            for term in medical_terms:
                if term not in unique_terms:
                    unique_terms.append(term)
            return " ".join(unique_terms)
        
        # If no medical terms found, return a simplified version of the query
        # Remove very common words
        stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", 
                     "you", "your", "yours", "yourself", "he", "him", "his", 
                     "she", "her", "hers", "it", "its", "they", "them", "their", 
                     "what", "which", "who", "whom", "this", "that", "these", 
                     "those", "am", "is", "are", "was", "were", "be", "been", 
                     "being", "have", "has", "had", "having", "do", "does", 
                     "did", "doing", "a", "an", "the", "and", "but", "if", "or", 
                     "because", "as", "until", "while", "of", "at", "by", "for", 
                     "with", "about", "against", "between", "into", "through", 
                     "during", "before", "after", "above", "below", "to", "from", 
                     "up", "down", "in", "out", "on", "off", "over", "under", 
                     "again", "further", "then", "once", "here", "there", "when", 
                     "where", "why", "how", "all", "any", "both", "each", "few", 
                     "more", "most", "other", "some", "such", "no", "nor", "not", 
                     "only", "own", "same", "so", "than", "too", "very", "can", 
                     "will", "just", "don", "should", "now", "feel", "feels", "feeling"]
        
        filtered_words = [w for w in words if w.lower() not in stop_words]
        if filtered_words:
            return " ".join(filtered_words[:5])  # Return at most 5 words
            
        return None
    
    def search_google_medical(self, query, limit=3):
        """Search Google for medical information from reputable sources"""
        try:
            # Check if Google API keys are available
            if not hasattr(self.config, 'google_api_key') or not hasattr(self.config, 'google_cse_id'):
                self.logger.warning("Google API keys not configured, skipping Google search")
                return []
                
            # Get API keys
            api_key = self.config.google_api_key
            cse_id = self.config.google_cse_id
            
            # Focus on reputable medical sites
            medical_sites = "site:nih.gov OR site:mayoclinic.org OR site:medlineplus.gov OR site:who.int"
            enhanced_query = f"{query} {medical_sites}"
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": cse_id,
                "q": enhanced_query,
                "num": limit
            }
            
            response = requests.get(url, params=params)
            results = response.json().get("items", [])
            
            formatted_results = []
            for item in results:
                formatted_results.append({
                    "title": item.get("title", ""),
                    "content": item.get("snippet", ""),
                    "source": item.get("displayLink", ""),
                    "url": item.get("link", "")
                })
                
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error in Google search: {str(e)}")
            return []
    
    def format_research_for_prompt(self, research_results):
        """Format research results for inclusion in a prompt"""
        if not research_results:
            return ""
            
        formatted_text = "### Relevant Medical Research:\n\n"
        
        for i, doc in enumerate(research_results):
            # Format title with source information
            formatted_text += f"**Source {i+1}: {doc.get('title', 'Untitled')}**\n"
            
            # Add publication details if available
            if doc.get('authors') and doc.get('journal') and doc.get('date'):
                formatted_text += f"*{doc.get('authors')} - {doc.get('journal')}, {doc.get('date')}*\n"
            
            # Add content with proper formatting
            content = doc.get('content', '')
            if len(content) > 500:
                content = content[:500] + "..."
                
            formatted_text += f"{content}\n\n"
            
            # Add URL if available
            if doc.get('url'):
                formatted_text += f"Reference: {doc.get('url')}\n\n"
        
        # Add a note about using the research
        formatted_text += "---\n"
        formatted_text += "*Note: Use the above research to inform your medical reasoning, but remember that each patient case is unique.*\n\n"
        
        return formatted_text
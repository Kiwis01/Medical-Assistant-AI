import re
from utils.imports import *

# Global dictionary to track images and their predictions
image_tracking = {}
generated_images = {}

# Global variables for conversation tracking
conversation_dir = None
timestamp = None

# Function to initialize conversation tracking
def init_conversation_tracking(config):
    """Initialize conversation tracking with timestamp and directory"""
    global conversation_dir, timestamp
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    conversation_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   "utils", "conversation_logs")
    
    # Create conversation directory if it doesn't exist
    if not os.path.exists(conversation_dir):
        os.makedirs(conversation_dir)
        config.logger.info(f"@common_utils.py Created conversation logs directory at {conversation_dir}")
    
    return conversation_dir, timestamp

# Function to save conversation history
def save_conversation(history, config, is_final=False):
    """Save conversation history to a JSON file"""
    global conversation_dir, timestamp
    
    if not conversation_dir or not timestamp:
        conversation_dir, timestamp = init_conversation_tracking(config)
    
    try:
        conversation_file = os.path.join(conversation_dir, f"conversation_{timestamp}.json")
        with open(conversation_file, 'w') as f:
            json.dump(history, f, indent=2)
        if is_final:
            print(f"Conversation saved to {conversation_file}")
        else:
            config.logger.info(f"@common_utils.py Auto-saved conversation to {conversation_file}")
        return conversation_file
    except Exception as e:
        config.logger.error(f"@common_utils.py Error saving conversation: {str(e)}")
        return None

# Function to handle program interruption
def setup_signal_handler(conversation_history, config):
    """Set up signal handler for graceful exit"""
    def signal_handler(sig, frame):
        print("\nSaving conversation before exit...")
        save_conversation(conversation_history, config, is_final=True)
        print("Exiting MedAI Assistant. Goodbye!")
        exit(0)
    
    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)
    return signal_handler

# Function to check if text contains an image file
def contains_image_file(text):
    image_pattern = re.compile(r'[\'\"]?([\w\-/\.]+\.(jpg|jpeg|png))[\'\"]?', re.IGNORECASE)
    match = image_pattern.search(text)
    if match:
        return match.group(1)  # Return the path without quotes
    return None

# Function to add an image and its prediction to tracking
def add_tracked_image(image_path, prediction, logger=None):
    """Add an image and its prediction to tracking"""
    image_tracking[image_path] = prediction
    if logger:
        logger.info(f"@common_utils.py Added image to tracking: {image_path}")
    
def is_image_tracked(image_path):
    """Check if an image has already been processed"""
    return image_path in image_tracking
    
def get_image_prediction(image_path):
    """Get prediction for a tracked image"""
    return image_tracking.get(image_path)

def add_generated_image(original_path, generated_path, logger=None):
    """Track a generated image for an original image"""
    generated_images[original_path] = generated_path
    if logger:
        logger.info(f"@common_utils.py Added generated image tracking: {original_path} -> {generated_path}")

def has_generated_image(original_path):
    """Check if an image already has a generated version"""
    return original_path in generated_images
    
def get_generated_image_path(original_path):
    """Get the path to the generated image"""
    return generated_images.get(original_path)
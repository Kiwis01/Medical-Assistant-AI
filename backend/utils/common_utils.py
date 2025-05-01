import re
from utils.imports import *

# Global dictionary to track images and their predictions
image_tracking = {}
generated_images = {}

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
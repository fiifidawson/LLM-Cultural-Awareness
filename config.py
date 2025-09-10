"""
Configuration and constants for LLM Cultural Awareness Evaluation
Based on the research paper: "Evaluating Cultural Awareness of LLMs for Yoruba, Malayalam, and English"
"""

import os
from pathlib import Path

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-api-key-here')
MODEL_NAME = "gpt-4o-mini"

# File Paths
BASE_DATA_PATH = '/link/to/base/path/CDEval_Data'
CACHE_FILE = os.path.join(BASE_DATA_PATH, 'computed_scores', 'computed_scores_openai.json')
RESULTS_FILE = os.path.join(BASE_DATA_PATH, 'final_results.json')

# Language Data Paths
LANGUAGE_PATHS = {
    "Malayalam": os.path.join(BASE_DATA_PATH, 'Malayalam'),
    "Yoruba": os.path.join(BASE_DATA_PATH, 'Yoruba'),
    "English": os.path.join(BASE_DATA_PATH, 'English')
}

# Cultural Dimensions
CULTURAL_DIMENSIONS = ["PDI", "IDV", "MAS", "UAI", "LTO", "IVR"]

# High scoring dimensions (Option 1 indicates higher score)
HIGH_SCORING_DIMENSIONS = {"PDI", "MAS", "UAI"}

# Low scoring dimensions (Option 2 indicates higher score)  
LOW_SCORING_DIMENSIONS = {"IDV", "LTO", "IVR"}

# Language-specific keys mapping
LANGUAGE_KEYS = {
    "English": {
        "question": "Question", 
        "option1": "Option 1", 
        "option2": "Option 2"
    },
    "Malayalam": {
        "question": "ചോദ്യം", 
        "option1": "ഓപ്ഷൻ 1", 
        "option2": "ഓപ്ഷൻ 2"
    },
    "Yoruba": {
        "question": "Ibeere", 
        "option1": "Aṣayan 1", 
        "option2": "Aṣayan 2"
    }
}

# Ground truth cultural dimension scores from the research paper
GROUND_TRUTH_SCORES = {
    "English": {
        "PDI": 0.40, "IDV": 0.60, "MAS": 0.62, 
        "UAI": 0.46, "LTO": 0.50, "IVR": 0.68
    },
    "Yoruba": {
        "PDI": 0.46, "IDV": 0.48, "MAS": 0.26, 
        "UAI": 0.41, "LTO": 0.70, "IVR": 0.36
    },
    "Malayalam": {
        "PDI": 0.21, "IDV": 0.48, "MAS": 0.21, 
        "UAI": 0.32, "LTO": 0.49, "IVR": 0.38
    }
}

# Evaluation Parameters
DEFAULT_REPETITIONS = 3
DEFAULT_TEMPERATURE = 0.7
MAX_TOKENS = 10
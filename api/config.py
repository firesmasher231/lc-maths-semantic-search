"""
Configuration settings for the LC Maths Question Search Web Application.
Modify these settings to customize the application behavior.
"""

# Server Configuration
HOST = "0.0.0.0"  # Set to '127.0.0.1' for localhost only
PORT = 5000  # Change if port 5000 is already in use
DEBUG = True  # Set to False for production

# Data Configuration
PAPERS_DIR = "data/papers"  # Directory containing PDF files
MAX_QUESTION_LENGTH = 800  # Maximum characters to display in search results

# Search Configuration
DEFAULT_NUM_RESULTS = 5  # Default number of search results
MAX_NUM_RESULTS = 20  # Maximum number of search results allowed
MIN_QUESTION_LENGTH = 30  # Minimum question length to include in search

# Model Configuration
SENTENCE_TRANSFORMER_MODEL = (
    "paraphrase-MiniLM-L3-v2"  # Much lighter model (~17MB vs ~80MB)
)

# UI Configuration
APP_TITLE = "LC Maths Question Search"
APP_SUBTITLE = "Search through Leaving Certificate Higher Level Mathematics papers using natural language"

# File Processing Configuration
SUPPORTED_FILE_EXTENSIONS = [".pdf"]  # Supported file types
CHUNK_SIZE = 1024 * 1024  # File reading chunk size (1MB)

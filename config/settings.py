"""
Application settings and environment configuration.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# DeepSeek API Configuration
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Firecrawl Configuration
FIRECRAWL_API_URL = "https://api.firecrawl.dev/v1"

# App Settings
APP_TITLE = "PaXth"
APP_ICON = "⚡"
APP_LAYOUT = "wide"

# Processing Settings
MAX_RETRIES = 3
REQUEST_TIMEOUT = 60  # seconds

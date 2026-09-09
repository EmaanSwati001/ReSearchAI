# backend/config.py

"""Configuration loader using python-dotenv.
Loads environment variables from a .env file in the project root.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file located at the project root (two levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOTENV_PATH = PROJECT_ROOT / ".env"
if DOTENV_PATH.exists():
    load_dotenv(dotenv_path=DOTENV_PATH)

# Example accessors (placeholders for future keys)
LLM_API_KEY = os.getenv("LLM_API_KEY")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")

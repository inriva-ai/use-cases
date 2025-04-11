import os
from pathlib import Path
from dotenv import load_dotenv

import logging
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

ROOT_DIR =  Path(__file__).resolve().parent.parent

def setup_openai_api_key():
    """Set up the OpenAI API key."""
    load_dotenv()
    # Retrieve the API key from the environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set it in the .env file.")
    os.environ["OPENAI_API_KEY"] = api_key

    # if not os.getenv("OPENAI_API_KEY"):
    #     os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
import os
from pathlib import Path
from dotenv import load_dotenv

import logging

import yaml

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


class Config:
    settings = None

    def __init__(self, config_path: str):
        self.config_path = config_path

    @classmethod
    def from_config_file(cls, config_path: str):
        instance = cls(config_path)
        instance._load()
        return instance

    def _load(self):
        """Load configuration from a YAML file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, "r") as file:
            Config.settings = yaml.safe_load(file)

    @classmethod
    def get(cls):
        if cls.settings is None:
            raise RuntimeError("Configuration not loaded. Call from_config_file() first.")
        return cls.settings

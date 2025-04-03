
# %%# Install dependencies
#%pip install -r requirements.txt
#%conda install --file requirements.txt

# Import required libraries
import os
from typing import Any

# Imports needed for MemoryCache setup
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache

# Imports from custom libraries
from core.config import ROOT_DIR, setup_openai_api_key
from core.summarizer import Summarizer
from core.json_schemas import json_schema_client,  json_schema_medical, patient_templates
from  core.ns_utils import initialize_database, delete_database, generate_patient_summary

# Imports for FastAPI
from contextlib import asynccontextmanager
from fastapi import FastAPI
import yaml

# Imports for logging
import logging
from logging.handlers import RotatingFileHandler

# Define constants
CONFIG_PATH = ROOT_DIR / "config/config.dev.yml"

class NoteSummarizerFastAPI(FastAPI):
 
    def __init__(self, config_path: str, *args, **kwargs):
        # Initialize the parent FastAPI class
        super().__init__(*args, **kwargs)

        # Load configuration
        self.config = self._load_config(config_path)

        # Set up logging
        self._setup_logging()

        # Define app attributes
        self.title= self.config.get("app", {}).get("name", "Note Summarizer")
        self.version = self.config.get("app", {}).get("version", "1.0.0")
        self.db_path = ROOT_DIR / self.config.get("database", {}).get("path", "db/database.db")
        self.data_dir = ROOT_DIR / self.config.get("database", {}).get("data_dir", "data")
 
    def _load_config(self, config_path: str):
        """Load configuration from a YAML file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    def _setup_logging(self):
        """Set up logging based on the configuration."""
        log_file = self.config.get("logging", {}).get("file", "./logs/app.log")
        log_level = self.config.get("logging", {}).get("level", "INFO").upper()
        max_log_size = self.config.get("logging", {}).get("max_size", 5 * 1024 * 1024)  # Default: 5 MB
        backup_count = self.config.get("logging", {}).get("backup_count", 3)  # Default: 3 backups

        # Ensure the log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Configure RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_log_size, backupCount=backup_count
        )
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # Set up the root logger
        logger = logging.getLogger()
        logger.setLevel(log_level)
        logger.addHandler(file_handler)

        # Log initialization message
        logging.info("FAST API app logging system initialized.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try :
        # Set up the OpenAI API key
        setup_openai_api_key()

        # Set up the cache
        set_llm_cache(InMemoryCache())
        
        # Initialize the database
        initialize_database(db_path=app.db_path, data_dir=app.data_dir)
           
        # Initialize the Summarizer
        app.state.note_summarizer = Summarizer(db_path=app.db_path)
        logging.info("Summarizer initialized successfully.")

        yield
    except Exception as e:
        logging.error(f"Error during app initialization: {e}")
    finally:
        # Delete the database and clean up resources
        if hasattr(app.state, "note_summarizer"):
            app.state.note_summarizer.dispose()
            logging.info("note_summarizer cleaned up.")
        delete_database(app.db_path)
        logging.info("Closing FastAPI app.")
  
# Initialize the FastAPI app with lifespan
# This function will run when the app starts and stops
app = NoteSummarizerFastAPI(config_path=CONFIG_PATH, lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": f"Welcome to {app.title}!"}

@app.get("/ingest")
def ingest_database():
    """Endpoint to initialize the database."""
    return initialize_database(db_path=app.db_path, data_dir=app.data_dir)

# API endpoint to generate a patient summary

# Request format
# request = {
#     "patient_info": {
#         "first_name": "Lupe126",
#         "last_name": "Rippin620"
#     },
#     "template_name": "allergies"
# }
@app.post("/answer")
def answer_question(request: dict[str, Any]):
    """Generate a patient summary using the template provided."""
    
    logging.info(f"Request: {request}")

    # Extract data from the request
    patient_info = request["patient_info"]
    template_name = request["template_name"]

    # Check if the template exists
    if template_name not in patient_templates:
        return {"error": f"Template '{template_name}' does not exist."}
    template = patient_templates[template_name]

    try:
        note_summary = generate_patient_summary(app.state.note_summarizer, patient_info=patient_info, template=template)
    except Exception as e:
        return {"error": str(e)}    
      
    return note_summary
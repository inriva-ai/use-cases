# Import required libraries
import os
import pandas as pd
import sqlite3
import json
import getpass
from dotenv import load_dotenv

# Imports needed for MemoryCache setup
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache

# Imports from custom libraries
from summarizer import Summarizer
from json_schemas import json_schema_client,  json_schema_medical, patient_templates

# Imports for FastAPI
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI
import yaml

# Imports for logging
import logging
from logging.handlers import RotatingFileHandler

# Define constants
CONFIG_PATH = "config.dev.yml"

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

def initialize_database(db_path, data_dir):
    """Initialize the SQLite database and import CSV files."""
    
    conn = sqlite3.connect(db_path)
    csv_files = [
        'allergies.csv', 'careplans.csv', 'claims.csv', 'claims_transactions.csv', 'conditions.csv',
        'devices.csv', 'encounters.csv', 'imaging_studies.csv', 'immunizations.csv', 'medications.csv',
        'observations.csv', 'organizations.csv', 'patients.csv', 'payer_transitions.csv', 'payers.csv',
        'procedures.csv', 'providers.csv', 'supplies.csv'
    ]
    for file in csv_files:
        table_name = file.split('.')[0]
        file_path = f'{data_dir}/{file}'
        df = pd.read_csv(file_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    logging.info(f"Database '{db_path}' initialized.")
    return {"message": "Database initialized and CSV files imported."}

# def delete_database(db_path):
#     """Delete the SQLite database file."""
#     try:
#         if os.path.exists(db_path):
#             os.remove(db_path)
#             logging.info(f"Database file '{db_path}' deleted successfully.")
#         else:
#             logging.info(f"Database file '{db_path}' does not exist.")
#     except Exception as e:
#         logging.error(f"Failed to delete database file: {e}")
#         return {"message": "Failed to Delete database file."}   
#     return {"message": "Database deleted."}    

def generate_patient_summary(note_summarizer, patient_info, template):
    """Generate a patient summary using all templates."""

    first_name = patient_info["first_name"]
    last_name = patient_info["last_name"]
    patient_details = f"first name: {first_name} last name: {last_name}"
    system_prompt = f"Patient {patient_details}."

    # Format patient details
    sql_prompt = template['sql_prompt'].format(patient_details=patient_details)
    logging.info(f"SQL Prompt: {sql_prompt}\n") 
     # print(f"SQL Prompt: {sql_prompt}\n")  # Debugging step

    query = note_summarizer.generate_sql_query(sql_prompt)
    logging.info(f"Generated SQL Query: {query}\n")
    # print(f"Generated SQL Query: {query}\n")  # Debugging step
    
    logging.info("Before executing query")
    data = note_summarizer.execute_query(query)
    logging.info("After executign query")

    user_prompt = note_summarizer.format_data(template["prompt"], data)
    logging.info(f"User Prompt: {user_prompt}\n")
    # print(f"User Prompt: {user_prompt}\n")  # Debugging step
    
    summary = note_summarizer.get_summary_from_openai(system_prompt, user_prompt)

    return summary


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
        self.db_path = self.config.get("database", {}).get("path", "./database.db")
        self.data_dir = self.config.get("database", {}).get("data_dir", "./data")

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
        logging.info("Logging system initialized.")


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
            del app.state.note_summarizer
            logging.info("note_summarizer cleaned up.")
        # delete_database(app.db_path)
        logging.info("Closing FastAPI app.")
  
# Initialize the FastAPI app with lifespan
# This function will run when the app starts and stops
app = NoteSummarizerFastAPI(config_path=CONFIG_PATH, lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": f"Welcome to {app.tilte}!"}

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
def answer_question(request: Dict[str, Any]):
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
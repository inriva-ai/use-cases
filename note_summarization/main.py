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
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Imports for logging
import logging


# Define constants
DATA_DIR = "./data"  # Directory with your CSVs
DB_PATH = "./healthcare_data.db"  # Path to your SQLite database

# Configure logging to write to a file
logging.basicConfig(
    # filename="fastapi.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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

def initialize_database():
    """Initialize the SQLite database and import CSV files."""
    conn = sqlite3.connect(DB_PATH)
    csv_files = [
        'allergies.csv', 'careplans.csv', 'claims.csv', 'claims_transactions.csv', 'conditions.csv',
        'devices.csv', 'encounters.csv', 'imaging_studies.csv', 'immunizations.csv', 'medications.csv',
        'observations.csv', 'organizations.csv', 'patients.csv', 'payer_transitions.csv', 'payers.csv',
        'procedures.csv', 'providers.csv', 'supplies.csv'
    ]
    for file in csv_files:
        table_name = file.split('.')[0]
        file_path = f'{DATA_DIR}/{file}'
        df = pd.read_csv(file_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    return {"message": "Database initialized and CSV files imported."}

def delete_database():
    """Delete the SQLite database file."""
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            logging.info(f"Database file '{DB_PATH}' deleted successfully.")
        else:
            logging.info(f"Database file '{DB_PATH}' does not exist.")
    except Exception as e:
        logging.error(f"Failed to delete database file: {e}")
        return {"message": "Failed to Delete database file."}   
    return {"message": "Database deleted."}    

def generate_patient_summary(note_summarizer, template, first_name, last_name):
    """Generate a patient summary using all templates."""
    patient_details = f"first name: {first_name} last name: {last_name}"
    system_prompt = f"Patient {patient_details}."

    # Format patient details
    sql_prompt = template['sql_prompt'].format(patient_details=patient_details)
    # print(f"SQL Prompt: {sql_prompt}\n")  # Debugging step
    query = note_summarizer.generate_sql_query(sql_prompt)
    # print(f"Generated SQL Query: {query}\n")  # Debugging step
    data = note_summarizer.execute_query(query)
    user_prompt = note_summarizer.format_data(template["prompt"], data)
    # print(f"User Prompt: {user_prompt}\n")  # Debugging step
    summary = note_summarizer.get_summary_from_openai(system_prompt, user_prompt)

    return summary

@asynccontextmanager
async def lifespan(app: FastAPI):
    try :
        setup_openai_api_key()
        logging.info("OpenAI API key setup successfully.")
        yield
    except Exception as e:
        logging.error(f"Error during app initialization: {e}")
    finally:
        if hasattr(app.state, "note_summarizer"):
            del app.state.note_summarizer
            logging.info("note_summarizer cleaned up.")
        delete_database()
        logging.info("Closing FastAPI app.")
  
# Initialize the FastAPI app with lifespan
# This function will run when the app starts and stops
app = FastAPI(lifespan=lifespan)

app.get("/")
def read_root():
    return {"message": "Welcome!"}

@app.get("/ingest")
def ingest_database():
    """Endpoint to initialize the database."""
    return initialize_database()


@app.get("/purge")
def purge_database():
    """Endpoint to purge the database."""
    return delete_database()

# Define a Pydantic model for input validation
class PatientSummary(BaseModel):
    first_name: str
    last_name: str
    template_name: str

# API endpoint to generate a patient summary
@app.post("/answer")
def answer_question(request: PatientSummary):
    """Generate a patient summary using the template provided."""
    try:
        if not hasattr(app.state, "note_summarizer"):
            app.state.note_summarizer = Summarizer(db_path=DB_PATH, json_schema_client=json_schema_client)
            logging.info("note_summarizer initialized at the endpoint level.")
        else:
            logging.info("note_summarizer already initialized.")
    except Exception as e:
        logging.error(f"Error initializing note_summarizer: {e}")
        return {"error": str(e)}        

    first_name = request.first_name
    last_name = request.last_name
    template_name = request.template_name

    # Check if the template exists
    if template_name not in patient_templates:
        return {"error": f"Template '{template_name}' does not exist."}

    template = patient_templates[template_name]
    try:
        note_summary = generate_patient_summary(app.state.note_summarizer, template, first_name, last_name)
    except Exception as e:
        return {"error": str(e)}      
    return note_summary

    


# Import required libraries
import os
import logging
import pandas as pd
from typing import Any
import sqlite3
from core.summarizer import Summarizer

def initialize_database(db_path: str, data_dir: str):
    """Initialize the SQLite database and import CSV files."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
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

def delete_database(db_path: str):
    """Delete the SQLite database file if it exists, with error handling."""
    if os.path.isfile(db_path):
        try:
            os.remove(db_path)
            logging.info(f"Deleted database file: {db_path}")
        except Exception as e:
            logging.error(f"Error deleting {db_path}: {e}")
    else:
        logging.info(f"No database file found at: {db_path}")

def generate_patient_summary(note_summarizer: Summarizer, patient_info: dict[str, Any], template: str):
    """Generate a patient summary using all templates."""
    first_name = patient_info["first_name"]
    last_name = patient_info["last_name"]
    patient_details = f"first name: '{first_name}' last name: '{last_name}'"
    system_prompt = f"Patient first name: {first_name} last name: {last_name}."

    # Format patient details
    sql_prompt = template['sql_prompt'].format(patient_details=patient_details)
    logging.info(f"SQL Prompt: {sql_prompt}") 
    
    query = note_summarizer.generate_sql_query(sql_prompt)
    logging.info(f"Generated SQL Query: {query}\n")
       
    # logging.info("Before executing query")
    data = note_summarizer.execute_query(query)
    logging.info(f"After executing query: {len(data)} rows returned")
    if len(data) == 0:
        raise ValueError(f"No data found for {patient_details}")

    user_prompt = note_summarizer.format_data(template["prompt"], data)
    #logging.info(f"User Prompt: {user_prompt}")
     
    summary = note_summarizer.get_summary_from_openai(system_prompt, user_prompt)

    return summary
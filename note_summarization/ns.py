
# %% [markdown]
# This notebook is designed to quickly demo major capabilities of the note summarization module without having to deploy and configure all the relevant components of the solution. The notebook:
# 1. Installs all necessary dependencies.
# 1. Creates a SQLite db file healthcare_data.db and ingests sample patient data from .csv files (located in a subfolder data) in the db.
# 2. Runs sample prompts for a specific patient to show case how [functional requirements](ref_design.md).

# To make run the notebook refer to additional information below.

# 1. **Install Dependencies**:
#     - The required dependencies are installed using a `requirements.txt` file.
# 2. **Import CSV Files into SQLite Database**:
#     - The CSV files are read from a specified directory and imported into a SQLite database named `healthcare_data.db`.
#     - Each CSV file is imported into a corresponding table in the database.

# 3. **Run Sample Prompts**:
#     - The OpenAI API key is set up using an environment variable.
#     - Templates for generating SQL queries and prompts for different patient data categories (e.g., medications, immunizations) are defined.
#     - A connection to the SQLite database is established.
#     - The LangChain `SQLDatabase` and OpenAI model (`ChatOpenAI`) are initialized.
#     - A chain is created to facilitate SQL query generation from natural language prompts.
#     - `generate_sql_query(template, first_name, last_name)`: Generates SQL queries based on the provided template and patient name.
#     - `execute_query(query)`: Executes the generated SQL query on the SQLite database and fetches the results.
#     - `format_data(template, data)`: Formats the extracted data into a specified template.
#     - `get_summary_from_openai(prompt)`: Sends a prompt to the OpenAI model and retrieves the response.
#     - `generate_patient_summary(first_name, last_name)`: Generates a summary for a patient using all defined templates. It involves generating SQL queries, executing them, formatting the data, and obtaining a summary from the OpenAI model.
#     - An example usage of the `generate_patient_summary` function is provided for a patient named "Lupe126 Rippin620".


# %%
# Install dependencies
#%pip install -r requirements.txt
#%conda install --file requirements.txt


# Import required libraries
import os
import pandas as pd
import sqlite3
import getpass
import json

# Imports needed for MemoryCache setup
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache

# Imports from custom libraries
from summarizer import Summarizer
from json_schemas import json_schema_client,  json_schema_medical

# Define constants
DATA_DIR = "./data"  # Directory with your CSVs
DB_PATH = "./healthcare_data.db"  # Path to your SQLite database

PATIENT_TEMPLATES = {
    "medications": {
        "name":  "medications",
        "sql_prompt": "What medications are prescribed to the patient {patient_details}? Retrieve ALL medications for the patient.",
        "prompt": "Summarize the patient's current medications:\n"

    },
    "symptoms": {
        "name":  "encounters",
        "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
        "prompt": "Provide an overview of the patient's reported symptoms and their progression over time:\n {encounters_rows}"
    },
    "physical_exam": {
        "name":  "physical_exam",
        "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
        "prompt": "What are the key points and key notes/observations from the patient's last physical examination?\n {physical_exam_rows}"
    },
    "consultation": {
        "name":  "consultation",
        "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
        "prompt": "What are the key findings from the patient's last non well-visit consultation note?\n {consultation_rows}"
    },
    "immunizations": {
        "name":  "immunizations",
        "sql_prompt" : "Retrieve ALL immunizations for the patient {patient_details}.", 
        "prompt": "Summarize the patient's immunizations:\n {immunizations_rows}"
    },
    "allergies": {
        "name":  "allergies",
        "sql_prompt": "In a single query retrieve ALL noted allergies or adverse reactions information for the patient {patient_details}.",
        "prompt": "Highlight any noted allergies or adverse reactions documented in the patient's records.\n {allergies_rows}"
    },
}
#    "history": "Summarize the patient's medical history relevant to their current condition.",
#    "chronic_conditions": "Highlight any chronic conditions and their management plans documented in the patient's history.",
#    "procedures": "Summarize the patient's relevant procedures and surgeries.",

# %%
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
    
def setup_openai_api_key():
    """Set up the OpenAI API key."""
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
  
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

# %%
# Main execution
if __name__ == "__main__":
    initialize_database()
    setup_openai_api_key()
   
   # Set up the cache
    set_llm_cache(InMemoryCache())

    first_name = "Lupe126"
    last_name = "Rippin620"
    print(f"\nGenerating summary for {first_name} {last_name}\n")

    note_summarizer = Summarizer(db_path=DB_PATH, json_schema_client=json_schema_medical)

    for key, template in PATIENT_TEMPLATES.items():
        try:
            print("=====================================")
            print(f"{key}")
            print("=====================================")
            # print(template["sql_prompt"])
            # print(template["prompt"])
            note_summary = generate_patient_summary(note_summarizer, template, first_name, last_name)
            ns_filename = f"./output/note_summary_{key}_{first_name}_{last_name}.json"
            with open(ns_filename, "w") as file:
                json.dump(note_summary, file, indent=4)
        except Exception as e:
            print(f"Error: {e}")
    del note_summarizer
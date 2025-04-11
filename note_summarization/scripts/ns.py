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
import json
import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Imports needed for MemoryCache setup
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache

## Imports from custom libraries
from core.config import ROOT_DIR, setup_openai_api_key
from core.summarizer import Summarizer
from core.json_schemas import json_schema_client,  json_schema_medical, patient_templates
from core.ns_utils import initialize_database, delete_database, generate_patient_summary

# Define constants
DATA_DIR = ROOT_DIR / "data"  # Directory with your CSVs
DB_PATH = ROOT_DIR / "db/healthcare_data.db"  # Path to your SQLite database

# %%
# Main execution
if __name__ == "__main__":
    initialize_database(db_path=DB_PATH, data_dir=DATA_DIR)
    setup_openai_api_key()
   
   # Set up the cache
    set_llm_cache(InMemoryCache())

    first_name = "Lupe126"
    last_name = "Rippin620"
    print(f"\nGenerating summary for {first_name} {last_name}\n")

    patient_info = {"first_name": first_name, "last_name": last_name}
    note_summarizer = Summarizer(db_path=DB_PATH, json_schema_client=json_schema_medical)

    for key, template in patient_templates.items():
        try:
            print("=====================================")
            print(f"{key}")
            print("=====================================")
            # print(template["sql_prompt"])
            # print(template["prompt"])
            note_summary = generate_patient_summary(note_summarizer, patient_info=patient_info, template=template)
            ns_filename = f"./output/note_summary_{key}_{first_name}_{last_name}.json"
            with open(ns_filename, "w") as file:
                json.dump(note_summary, file, indent=4)
        except Exception as e:
            print(f"Error: {e}")
    delete_database(db_path=DB_PATH)        
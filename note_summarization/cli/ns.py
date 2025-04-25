# %% [markdown]
# This script is designed to quickly demo major capabilities of the note summarization module without having to deploy and configure all the relevant components of the solution.
# The script:
# 1. Installs all necessary dependencies.
# 1. Creates a SQLite db file healthcare_data.db and ingests sample patient data from .csv files (located in a data folder) in the db.
# 2. Runs sample prompts for a specific patient and save the outputs into JSON files.


# %%
# Install dependencies
#%pip install -r requirements.txt
#%conda install --file requirements.txt


# Import required libraries
import json

# Set up logging if needed
# Uncomment the following lines to enable logging
# import logging
# logging.basicConfig(level=logging.INFO, format="%(message)s")

# Imports needed for MemoryCache setup
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache

# Imports from custom libraries
from core.config import ROOT_DIR, setup_openai_api_key
from core.summarizer import Summarizer
from core.ns_utils import initialize_database, delete_database, generate_patient_summary
from core.json_schemas import patient_templates

# Define constants
DATA_DIR = ROOT_DIR / "data"  # Directory with your CSVs
DB_PATH = ROOT_DIR / "db/healthcare_data.db"  # Path to your SQLite database
OUTPUT_DIR = ROOT_DIR / "output"  # Directory for output files


def generate_note_summarization(note_summarizer, patient_info, template_id, template):
    """Generate a summary for a specific patient using the provided template."""
    try:
        print(f"Processing template: {template["name"]}")
        note_summary = generate_patient_summary(note_summarizer, patient_info=patient_info, template=template)
        ns_filename = OUTPUT_DIR / f"note_summary_{template_id}_{patient_info["first_name"]}_{patient_info["last_name"]}.json"
        with open(ns_filename, "w") as file:
            json.dump(note_summary, file, indent=4)
        print(f"Summary saved to {ns_filename}\n")
    except Exception as e:
        print(f"Error processing template {template["name"]}: {e}\n")

# Main execution
if __name__ == "__main__":
    # Initialize the database
    initialize_database(db_path=DB_PATH, data_dir=DATA_DIR)
    print("Database initialized successfully.")

    # Set up OpenAI API key and cache
    setup_openai_api_key()
    set_llm_cache(InMemoryCache())

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Define patient information
    first_name = "Lupe126"
    last_name = "Rippin620"
    print(f"\nGenerating summary for {first_name} {last_name}\n")

    # Comment out one of the lines to run script either for a particuar template or for all templates
    # template_id = "medications"
    template_id = None

    patient_info = {"first_name": first_name, "last_name": last_name}
    note_summarizer = Summarizer(db_path=DB_PATH)

    if template_id:
        generate_note_summarization(note_summarizer, patient_info, template_id, patient_templates[template_id])
    else:    
        # Generate summaries for all templates
        for key, template in patient_templates.items():
            generate_note_summarization(note_summarizer, patient_info, key, template)

    # Close the database connection
    note_summarizer.dispose()     

    # Delete the database
    delete_database(db_path=DB_PATH)
    print("Database deleted successfully.")
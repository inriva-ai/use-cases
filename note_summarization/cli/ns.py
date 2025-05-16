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
from core.template_library import patient_templates, sql_templates
from core.ns_utils import NoteSummarizationUtils as ns_utils  

# Define constants
DATA_DIR = ROOT_DIR / "data"  # Directory with your CSVs
DB_PATH = ROOT_DIR / "db/healthcare_data.db"  # Path to your SQLite database
OUTPUT_DIR = ROOT_DIR / "output"  # Directory for output files

# Uncomment the following lines to enable logging/debugging
# import logging
# logging.basicConfig(
#     level=logging.INFO,  # Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR)
#     format="%(asctime)s - %(levelname)s - %(message)s",  # Customize the log format
#     handlers=[logging.StreamHandler()]  # Add a StreamHandler to output logs to the console
# )

def create_patient_note_summary(note_summarizer, patient_info, template_id, custom_prompt=None):
    """Generate a summary for a specific patient using the provided template."""

    # Check if the template ID is valid
    if template_id not in patient_templates:
        print(f"Invalid template ID: {template_id}")
        print("Available templates:")
        for template_id in patient_templates:
            print(f"- {template_id}: {patient_templates[template_id]['name']}")
        return
    
    # Load the template
    template = patient_templates[template_id].copy()
    print(f"Processing template: {template['name']}")

    # Custom template handling
    is_custom_prompt = False
    if template_id == "custom":
        is_custom_prompt = True
        if not custom_prompt:
            print("Custom template requires a prompt.")
            return
        
        print(f"Custom Prompt: {custom_prompt}")
        template["prompt"] = custom_prompt
        try: 
            template["sql_prompts"] = note_summarizer.generate_sql_prompts(custom_prompt, sql_templates)
        except Exception as e:
            print(f"Error generating sql prompts list for the custom prompt: {e}") 
            return 

        if not template["sql_prompts"]:
            print("Insufficient information to answer the question.")
            return
        else:
            print(f"Selected SQL prompts: {template['sql_prompts']}")

    template = ns_utils.populate_tempalate(template, is_custom_prompt=is_custom_prompt)  
       
    try:
        note_summary = ns_utils.generate_patient_summary(note_summarizer, patient_info=patient_info, template=template)
    except Exception as e:
        print(f"Error processing template {template['name']}: {e}")
        return
    
    ns_filename = OUTPUT_DIR / f"note_summary_{template_id}_{patient_info['first_name']}_{patient_info['last_name']}.json"
    with open(ns_filename, "w") as file:
        json.dump(note_summary, file, indent=4)
    print(f"Summary saved to {ns_filename}")
    
# Main execution
if __name__ == "__main__":
    # Initialize the database
    ns_utils.initialize_database(db_path=DB_PATH, data_dir=DATA_DIR)
    print("Database initialized successfully.")

    # Set up OpenAI API key and cache
    setup_openai_api_key()
    set_llm_cache(InMemoryCache())

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Define patient information
    first_name = "Lupe126"
    last_name = "Rippin620"
    print(f"\nGenerating Note Summary for patient {first_name} {last_name}\n")

    # Comment out one of the lines to run script either for a particuar template or for all templates
    
    # template_id = None
    template_id = "custom"
    #template_id = "medications"

    # custom_prompt = "What are the patient's previous surgical procedures and outcomes?"
    # custom_prompt = "Summarize any pending labs, imaging, referrals, or insurance-related items that require follow-up."
    # custom_prompt = "Summarize this patient’s history related to heart conditions."
    custom_prompt = "Summarize this patient’s history related to diabetes."
    # custom_prompt = "Summarize this patient’s history related to hypertension."
    # custom_prompt = "Highlight potential risk factors such as high fall risk, polypharmacy, hospice eligibility, or frequent hospitalizations"

    patient_info = {"first_name": first_name, "last_name": last_name}
    note_summarizer = Summarizer(db_path=DB_PATH)

    if template_id:
        create_patient_note_summary(note_summarizer, patient_info, template_id, custom_prompt)
    else:    
        # Generate summaries for all templates
        for template_id in patient_templates:
            create_patient_note_summary(note_summarizer, patient_info, template_id, custom_prompt)

    # Close the database connection
    note_summarizer.dispose()     

    # Delete the database
    ns_utils.delete_database(db_path=DB_PATH)
    print("\nDatabase deleted successfully.")
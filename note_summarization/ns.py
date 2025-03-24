
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
import sqlite3
import pandas as pd
import getpass
import json
from json_schemas import json_schema_sql, json_schema_client

from langchain_community.utilities.sql_database import SQLDatabase
# Different implementation of ChatOpenAI will be usied to avoid "with_structured_output is not implemented for this model" error
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import SystemMessage, HumanMessage

# Define constants
DATA_DIR = "./data"  # Directory with your CSVs
DB_PATH = "./healthcare_data.db"  # Path to your SQLite database

PATIENT_TEMPLATES = {
    "medications": {
        "name":  "medications",
        "sql_prompt": "What medications are prescribed to the patient {patient_details}? Retrieve ALL medications for the patient.",
        "prompt": "Summarize the patient's current medications:\n {medications_rows}"
    },
    "symptoms": {
        "name":  "encounters",
        "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
        "prompt": "Provide an overview of the patient's reported symptoms and their progression over time:\n {encounters_rows}"
    },
    "immunizations": {
        "name":  "immunizations",
        "sql_prompt" : "Retrieve ALL immunizations for the patient {patient_details}.", 
        "prompt": "Summarize the patient's immunizations:\n {immunizations_rows}"
    },
    "physical_exam": {
        "name":  "physical_exam",
        "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
        "prompt": "What are the key points and key notes/observations from the patient's last physical examination?\n {physical_exam_rows}"
    },
    "allergies": {
        "name":  "allergies",
        "sql_prompt": "In a single query retrieve ALL noted allergies or adverse reactions information for the patient {patient_details}.",
        "prompt": "Highlight any noted allergies or adverse reactions documented in the patient's records.\n {allergies_rows}"
    },
    "consultation": {
        "name":  "consultation",
        "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
        "prompt": "What are the key findings from the patient's last non well-visit consultation note?\n {consultation_rows}"
    },
}
#    "history": "Summarize the patient's medical history relevant to their current condition.",
#    "chronic_conditions": "Highlight any chronic conditions and their management plans documented in the patient's history.",
#    "procedures": "Summarize the patient's relevant procedures and surgeries.",

# %%
# define NoteSummarization class
class NoteSummarization:
    def __init__(self, db_path=DB_PATH, model_name="gpt-4o", temperature=0):
        '''Constructor for the NoteSummarization class'''
        self.db_path = db_path
        self.conn = None
        self.db = None
        self.llm = None
        self.model_name = model_name
        self.temperature = temperature
        self.structured_llm_sql = None
        self.structured_llm_client = None
        self.system_sql_prompt = None
        self.system_client_prompt = "Patient {patient_details}."
                
        self._initialize_db_connection()
        self._initialize_llm_model()
        self._initialize_prompt()

        if self.conn is None or self.db is None:
            raise ValueError("Database connection not initialized.")


    def __del__(self):
        '''Destructor for the NoteSummarization class'''
        # Close the SQLite database connection
        if self.conn:
            self.conn.close()

    def _initialize_db_connection(self):
            """Initialize the SQLite database connection and LangChain SQLDatabase."""
            self.conn = sqlite3.connect(self.db_path)
            self.db = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")

    def _initialize_llm_model(self):
        """Initialize the OpenAI model."""
        self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)
        self.structured_llm_sql = self.llm.with_structured_output(json_schema_sql, method="json_schema")
        self.structured_llm_client = self.llm.with_structured_output(json_schema_client, method="json_schema")

    def _initialize_prompt(self):
        """Create a custom prompt template for structured output."""

        sqlite_prompt = """You are a SQLite expert. Given an input question, create a syntactically correct SQLite query to run. 
        The database schema consists of multiple tables, each containing different columns.
        Never query for all columns from a table. You must query only the columns that are needed to answer the question. 
        For each question, assume you know NOTHING except the schema provided.
        Use only the information explicitly provided in the input question and schema. Do not make any assumptions. Do not use any memorized or cached data.
        Use JOINs when data from multiple tables are required, ensuring that relationships between tables are explicitly defined. Always define explicit ON conditions for JOINs to prevent Cartesian products.
        Wrap each column name in double quotes (") to denote them as delimited identifiers.
        Pay attention to use only the column names you can see in the tables provided. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
        Pay attention to use date('now') function to get the current date, if the question involves "today".
        Return only the SQL query as the answer. Do not include any explanations, formatting, or additional text.

        Only use the following tables: {table_info}

        Question: {input}
        """
        self.system_sql_prompt = PromptTemplate(
            input_variables=["input", "table_info"],
            template=sqlite_prompt
        )       
 
    def generate_sql_query(self, template, patient_details):
        """Generate SQL query, ensuring it is patient-specific."""
        # Format patient details
        user_sql_prompt = self.system_client_prompt.format(patient_details=patient_details) + template['sql_prompt'].format(patient_details=patient_details)
        
        # Generate SQL from text query
        chain = self.system_sql_prompt | self.structured_llm_sql
        inputs = {
            "input": user_sql_prompt,
            "table_info": self.db.get_table_info()
        }
        response = chain.invoke(inputs)
        sql_query = response['sql']

        # print(f"Generated SQL query: {sql_query}")  # Debugging step

        return sql_query

    def execute_query(self, query):
        """Execute SQL query on SQLite database and fetch results."""
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def format_data(self, template, data):
        """Format extracted data into the template."""
        formatted_rows = "\n".join([", ".join(map(str, row)) for row in data])
        entity_name = template["name"]
        return template["prompt"].replace(f"{{{entity_name}_rows}}", formatted_rows)

    def get_summary_from_openai(self, prompt, patient_details):
        """Send prompt to OpenAI model and get a response."""
        # Create a list of BaseMessages
        messages = [
            SystemMessage(content=self.system_client_prompt.format(patient_details=patient_details)),
            HumanMessage(content=prompt)
        ]

        # Invoke the structured LLM client with the list of messages
        response = self.structured_llm_client.invoke(messages)

        # Return the content of the response
        return response
        # response = self.structured_llm_client.client.create(
        #     model=self.model_name,
        #     messages=[
        #         {"role": "system", "content": self.system_client_prompt.format(patient_details=patient_details)},
        #         {"role": "user", "content": prompt}
        #     ]
        # )
        # return response.choices[0].message.content

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
        # Uncomment the line below to prompt for the API key
        api_key = getpass.getpass("Enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = api_key

def generate_patient_summary(note_summarizer, template, first_name, last_name):
    """Generate a patient summary using all templates."""
    patient_details = f"first name: {first_name} last name: {last_name}"
    query = note_summarizer.generate_sql_query(template, patient_details)
    data = note_summarizer.execute_query(query)
    formatted_prompt = note_summarizer.format_data(template, data)
    summary = note_summarizer.get_summary_from_openai(formatted_prompt, patient_details)
    return summary

# %%
# Main execution
if __name__ == "__main__":
    initialize_database()
    setup_openai_api_key()
   
    first_name = "Lupe126"
    last_name = "Rippin620"
    print(f"Generating summary for {first_name} {last_name}\n")

    note_summarizer = NoteSummarization()
    for key, template in PATIENT_TEMPLATES.items():
        try:
            print("=====================================")
            print(f"{key}")
            print("=====================================")
            # print(template["sql_prompt"])
            # print(template["prompt"])
            note_summary = generate_patient_summary(note_summarizer, template, first_name, last_name)
            ns_filename = f"note_summary_{key}_{first_name}_{last_name}.json"
            with open(ns_filename, "w") as file:
                json.dump(note_summary, file, indent=4)
        except Exception as e:
            print(f"Error: {e}")
    del note_summarizer
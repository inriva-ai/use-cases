
# %%
from __future__ import annotations
import warnings

# Install dependencies
#%pip install -r requirements.txt
#%conda install --file requirements.txt

# Import required libraries
import os
import pandas as pd
import sqlite3
import getpass
import json

# imports needed for SQLiteChain class
from typing import Any, Dict
from pydantic import Field
from langchain_core.language_models import BaseLanguageModel
from langchain.prompts.prompt import PromptTemplate

# imports needed for Summarizer class
from langchain_community.utilities.sql_database import SQLDatabase
# Different implementation of ChatOpenAI will be usied to avoid "with_structured_output is not implemented for this model" error
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# Schemas for LLM structured output
from json_schemas import json_schema_client

# %%
# Define SQLiteChain class
class SQLiteChain:
    """Chain for interacting with SQLite Database.

    Example:
        .. code-block:: python

            from langchain.prompts.prompt import PromptTemplate
            from langchain_community.utilities.sql_database import SQLDatabase
            from langchain_openai import ChatOpenAI
            db = SQLDatabase(...)
            db_chain = SQLiteChain.from_llm(OpenAI(), db)

    """
    llm: BaseLanguageModel
    """LLM for SQL generation."""
    database: SQLDatabase = Field(exclude=True)
    """SQL Database to connect to."""
    system_prompt: str = "query" #: :meta private:
    """System prompt for the LLM."""

    def __init__(self, llm, db):
        """
        Initialize the SQLiteChain with the required components.
        
        Args:
            db (SQLDatabase): The database object to retrieve schema information.
            llm (LLM): LLM for SQL generation.
        """
        self.llm = llm
        self.db = db
        self.system_prompt = None
        self._initialize_prompt()

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
        self.system_prompt = PromptTemplate(
            input_variables=["input", "table_info"],
            template=sqlite_prompt
        )

    def invoke(self, prompt)-> Dict[str, Any]:
        """
        Generate SQL query from a natural language prompt.
        
        Args:
            prompt (str): The natural language prompt to generate the SQL query.

        Returns:
            dict: The response containing the generated SQL query.
        """
        # Combine the system prompt and structured LLM
        chain = self.system_prompt | self.llm

        # Prepare inputs
        inputs = {
            "input": prompt,
            "table_info": self.db.get_table_info()
        }

        # Invoke the chain
        response = chain.invoke(inputs)
        return response
    
# %%
# Define Summarizer class
class Summarizer:
    def __init__(self, db_path, model_name="gpt-4o", temperature=0, json_schema_client=json_schema_client):
        """Constructor for the Summarizer class"""
        self.db_path = db_path
        self.conn = None
        self.db = None
        self.llm = None
        self.model_name = model_name
        self.temperature = temperature
        self.json_schema_client = json_schema_client
        self.db_chain = None
        self.structured_llm_sql = None
        self.structured_llm_client = None

        self._initialize_db_connection()
        self._initialize_llm_models()

        if self.conn is None or self.db is None:
            raise ValueError("Database connection not initialized.")

    def __del__(self):
        """Destructor for the Summarizer class'"""
        # Close the SQLite database connection
        if self.conn:
            self.conn.close()

    def _initialize_db_connection(self):
        """Initialize the SQLite database connection and LangChain SQLDatabase."""
        self.conn = sqlite3.connect(self.db_path)
        self.db = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")

    def _initialize_llm_models(self):
        """Initialize the OpenAI model."""
        json_schema_sql = {
            "title": "sql_query",
            "description": "SQL query to retrieve data from a database.",
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "The SQL query to retrieve data from the database."
                },
            
            },
        }
        self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)
        self.structured_llm_sql = self.llm.with_structured_output(json_schema_sql, method="json_schema")
        self.structured_llm_client = self.llm.with_structured_output(self.json_schema_client, method="json_schema")
        self.db_chain = SQLiteChain(llm=self.structured_llm_sql, db=self.db)
    
    def generate_sql_query(self, prompt):
        """Generate SQL query"""
        response = self.db_chain.invoke(prompt)
        sql_query = response['sql']
        # print(f"Generated SQL query: {sql_query}")  # Debugging step
        return sql_query

    def execute_query(self, query):
        """Execute SQL query on SQLite database and fetch results."""
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def format_data(self, prompt, data):
        """Format extracted data into the prompt."""
        formatted_rows = "\n".join([", ".join(map(str, row)) for row in data])
        return f"{prompt} {formatted_rows}"

    def get_summary_from_openai(self, system_prompt, user_prompt):
        """Send prompt to OpenAI model and get a response."""
        # Create a list of BaseMessages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Invoke the structured LLM client with the list of messages
        response = self.structured_llm_client.invoke(messages)

        # Return the content of the response
        return response

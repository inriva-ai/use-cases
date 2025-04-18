
# %%
from __future__ import annotations

# imports needed for SQLiteChain class
from typing import Any
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
from core.json_schemas import json_schema_client
from sqlalchemy import text

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
    db: SQLDatabase = Field(exclude=True)
    """SQL Database to connect to."""
    system_prompt: PromptTemplate
    """System prompt for the LLM."""

    def __init__(self, llm: BaseLanguageModel, db: SQLDatabase):
        """
        Initialize the SQLiteChain with the required components.
        
        Args:
            db (SQLDatabase): The database object to retrieve schema information.
            llm (LLM): LLM for SQL generation.
        """
        self.llm = llm
        self.db = db
        self.system_prompt = self._initialize_prompt()
      
    def _initialize_prompt(self) -> PromptTemplate:
        """Create a custom prompt template for structured output."""

        sqlite_prompt = """You are a SQLite expert. Given an input question, create a syntactically correct SQLite query to run. 
        The database schema consists of multiple tables, each containing different columns.
        Never query for all columns from a table. You must query only the columns that are needed to answer the question. 
        For each question, assume you know NOTHING except the schema provided.
        Use only the information explicitly provided in the input question and schema. Do not make any assumptions. Do not use any memorized or cached data.
        Assume all input values are exactly as they are provided, and treat them as distinct and unique unless explicitly stated otherwise.
        Ensure that all comparisons use strict equality and do not rely on partial matches, similarity, or assumptions.
        Every character (including letters, numbers, and special characteres) in every input value is CRITICAL and and must be considered exactly as provided.
        Do not make any assumptions about misspellings, typos, or variations in input values.
        Do not interpret or infer relationships between input values unless explicitly defined in the schema or question. 
        Do not perform any transformations, approximations, or interpretations of input values.
        Treat all input values as independent and unrelated unless explicitly stated otherwise.
        Do not use any external knowledge or information. Do not use any external APIs or services. Do not use any external libraries or packages. Do not use any external files or resources.
        Wrap each column name in double quotes (") to denote them as delimited identifiers.
        Pay attention to use only the column names you can see in the tables provided. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
        Pay attention to use date('now') function to get the current date, if the question involves "today".
        Return only the SQL query as the answer. Do not include any explanations, formatting, or additional text.

        Only use the following tables: {table_info}

        Question: {input}
        """
        system_prompt = PromptTemplate(
            input_variables=["input", "table_info"],
            template=sqlite_prompt
        )
        return system_prompt

    def invoke(self, prompt: str) -> dict[str, Any]:
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
    def __init__(self, db_path: StopIteration, pool_size: int=5,  model_name: str="gpt-4o", temperature: int=0, json_schema_client: dict[str, Any]=json_schema_client):
        """Constructor for the Summarizer class"""

        self.db = self._initialize_db_connection(db_path=db_path, pool_size=pool_size)
        if self.db is None:
            raise ValueError("Database connection not initialized.")
        
        self.llm = None
        self.db_chain = None
        # self.structured_llm_sql = None
        # self.structured_llm_client = None
        # self._initialize_llm_models(model_name=model_name, temperature=temperature, json_schema_client=json_schema_client)
        self._initialize_llm(model_name=model_name, temperature=temperature)
        
    def dispose(self):
        """Dispose of the SQLite database connection."""
        # Dispose of the engine to free up resources
        # FIXME: This is a temporary fix to avoid "AttributeError: 'SQLDatabase' object has no attribute '_engine'" error        
        if hasattr(self.db, "_engine"):
            self.db._engine.dispose()

    def _initialize_db_connection(self, db_path: str, pool_size: int) -> SQLDatabase:
        """Initialize the SQLite database connection and LangChain SQLDatabase."""
        db = SQLDatabase.from_uri(f"sqlite:///{db_path}", engine_args = {"pool_size": pool_size})
        return db
              
    def _initialize_llm(self, model_name: str, temperature: int) -> None:
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
        # FIXME: using method="json_schema" would require additional compliance with OpenAI specifications:
        # https://platform.openai.com/docs/guides/structured-outputs/supported-schemas?api-mode=chat
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        structured_llm = self.llm.with_structured_output(json_schema_sql)#, method="json_schema")
        #self.structured_llm_client = self.llm.with_structured_output(json_schema_client)#, method="json_schema")
        self.db_chain = SQLiteChain(llm=structured_llm, db=self.db)
    
    def generate_sql_query(self, prompt: str) -> str:
        """Generate SQL query"""
        response = self.db_chain.invoke(prompt)
        sql_query = response['sql']
        # print(f"Generated SQL query: {sql_query}")  # Debugging step
        return sql_query

    def execute_query(self, query: str) -> Any:
        """Execute SQL query on SQLite database and fetch results."""
        cursor = self.db.run(command = query, fetch="cursor")
        rows = cursor.all()
        cursor.close()
        return rows

    def format_data(self, prompt: str, data: Any) -> str:
        """Format extracted data into the prompt."""
        formatted_rows = "\n".join([", ".join(map(str, row)) for row in data])
        return f"{prompt}{formatted_rows}"

    def format_data(self, data: Any) -> str:
        """Format extracted data into the prompt."""
        formatted_rows = "\n".join([", ".join(map(str, row)) for row in data])
        return formatted_rows
    
    def generate_user_prompt(self, prompt: str, data: Any) -> str:
        """Format extracted data into the prompt."""
        return f"{prompt}{data}"
    
    def get_summary_from_openai(self, system_prompt: str, user_prompt: str, output_schema: dict[str, Any]) -> dict[str, Any]:
        """Send prompt to OpenAI model and get a response."""
        # Create a list of BaseMessages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        # Invoke the structured LLM client with the list of messages
        structured_llm = self.llm.with_structured_output(output_schema)
        response = structured_llm.invoke(messages)

        # Return the content of the response
        return response

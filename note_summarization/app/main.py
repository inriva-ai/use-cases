# %%# Install dependencies
#%pip install -r requirements.txt
#%conda install --file requirements.txt

# Import required libraries
import os
from pydantic import BaseModel

# Imports needed for MemoryCache setup
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache

# Imports from custom libraries
from core.config import ROOT_DIR, Config, setup_openai_api_key

from core.summarizer import Summarizer
#from core.json_schemas import  patient_templates
from core.template_library import patient_templates, prompt_templates, sql_templates, output_schemas
from  core.ns_utils import initialize_database, delete_database, generate_patient_summary

# Imports for FastAPI
import yaml
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

# Imports for logging
import logging
from logging.handlers import RotatingFileHandler

# For Endpoint error handling
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request, status

# Define constants
CONFIG_PATH = ROOT_DIR / "config/config.dev.yml"

# Custom filter for formatting dates
def datetimeformat(value, format='%m/%d/%Y'):
    return datetime.strptime(value, '%Y-%m-%d').strftime(format)

class NoteSummarizerFastAPI(FastAPI):
 
    def __init__(self, config_path: str, *args, **kwargs):
        # Initialize the parent FastAPI class
        super().__init__(*args, **kwargs)

        # Initialize configuration
        Config.from_config_file(config_path)
        self.config = Config.get()

        # Set up logging
        self._setup_logging()

        # Populate configuration settings
        self.title= self.config["app"]["name"]
        self.version = self.config["app"]["version"]
        self.db_path = ROOT_DIR / self.config["database"]["path"]
        self.data_dir = ROOT_DIR / self.config["database"]["data_dir"]

        # Load OpenAI API key from .env file
        setup_openai_api_key()

        # Set up OpenAI API key from the config file
        #os.environ["OPENAI_API_KEY"] = self.config["openai"]["api_key"]

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
        logging.info("FAST API app logging system initialized.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Set up the cache
        set_llm_cache(InMemoryCache())
        
        # Initialize the database
        if not os.path.exists(app.db_path):
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
            app.state.note_summarizer.dispose()
            logging.info("note_summarizer cleaned up.")
        if app.config.get("database", {}).get("delete_db", False):
            delete_database(app.db_path)
        logging.info("Closing FastAPI app.")
    
  
# Initialize the FastAPI app with lifespan
# This function will run when the app starts and stops
app = NoteSummarizerFastAPI(config_path=CONFIG_PATH, lifespan=lifespan)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Add the filter to Jinja2
templates.env.filters['datetimeformat'] = datetimeformat

@app.get("/")
def read_root():
    return {"message": f"Welcome to {app.title}!"}

@app.get("/ingest")
def ingest_database():
    """Endpoint to initialize the database."""
    return initialize_database(db_path=app.db_path, data_dir=app.data_dir)

@app.get("/templates")
def get_templates():
    """Endpoint to retrieve available templates."""
    return {"templates": sorted([(key, value["name"]) for key, value in patient_templates.items()])}


# API endpoint to generate a patient summary
# Request format
# request = {
#     "patient_info": {
#         "first_name": "Lupe126",
#         "last_name": "Rippin620"
#     },
#     "template_name": "allergies"
# }

@app.get("/answer", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "response": None})


class RequestBody(BaseModel):
    patient_info: dict
    template_name: str

@app.post("/answer")
async def answer_question(
        request_body: RequestBody = Body(..., description="Request body containing patient info and template name"),
        response_type: str = Query("html", description="Response type: 'html' or 'json'")
    ):
    """Generate a patient summary using the template provided."""
    
    data = request_body.model_dump()
    logging.info(f"Request received: {data}")

    # Extract data from the request
    patient_info = data.get("patient_info", {})
    template_name = data.get("template_name", "")

    # Validate patient_info fields
    if not patient_info.get("first_name") or not patient_info.get("last_name"):
        response = {"error": "Invalid patient_info: Missing first_name or last_name."}
        logging.error("Invalid patient_info: Missing first_name or last_name.")
        return _generate_response(data, response, response_type)

    # Check if the template exists
    if template_name not in patient_templates:
        response = {"error": f"Template '{template_name}' does not exist."}
        logging.error(f"Template '{template_name}' does not exist.")
        return _generate_response(data, response, response_type)
    
    template = _populate_tempalate(patient_templates[template_name])
    try:
        response = generate_patient_summary(app.state.note_summarizer, patient_info=patient_info, template=template)
        logging.info(f"Summary generated successfully for template: {template_name}")
    except Exception as e:
        response = {"error": str(e)}
        logging.error(f"Error generating summary for patient {patient_info}: {e}")
        return _generate_response(data, response, response_type)
         
    # Render only the output section of the template
    return _generate_response(data, response, response_type, template["output_template"])

def _populate_tempalate(template:dict)-> dict:
    """Format the template to be used to answer the question. Specificalliy, it will replace the prompt, sql_templates and output_schema with the actual templates:
    {
        "prompt",
        "sql_prompts": [],
        "output_schema",
        "output_template"
    }    
    """   
    populated_template = template.copy()
    populated_template["prompt"] = prompt_templates[template["prompt"]]
    populated_template["output_schema"] = output_schemas[template["output_schema"]]
    sql_prompts = template.get("sql_prompts", [])
    populated_template["sql_prompts"] = []
    for sql_prompt in sql_prompts:
        populated_template["sql_prompts"].append(sql_templates[sql_prompt])
    return populated_template

def _generate_response(request: Request, response: dict, response_type: str, output_template: str = None):
    """Helper function to generate the appropriate response based on response_type."""
    if response_type == "html" and output_template is not None:
        return templates.TemplateResponse(output_template + ".html", {"request": request, "response": response})
    return JSONResponse(content=response)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()  # Raw request body (bytes)
    print("🚨 Validation error:")
    print("Request body:", body.decode("utf-8"))
    print("Validation issues:", exc.errors())
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": body.decode("utf-8")
        }
    )

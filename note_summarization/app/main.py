# %%# Install dependencies
#%pip install -r requirements.txt
#%conda install --file requirements.txt

# Import required libraries
import os
from pydantic import BaseModel, Field

# Imports needed for MemoryCache setup
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache

# Imports from custom libraries
from core.config import ROOT_DIR, Config, setup_openai_api_key
from core.summarizer import Summarizer
from core.template_library import patient_templates, sql_templates
from  core.ns_utils import NoteSummarizationUtils as ns_utils 

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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Custom filter for Jinja dates formatting
def datetimeformat(value, format='%m/%d/%Y'):
    return datetime.strptime(value, '%Y-%m-%d').strftime(format)

# NoteSummarizerFastAPI class that extends FastAPI
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
            ns_utils.initialize_database(db_path=app.db_path, data_dir=app.data_dir)
           
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
            ns_utils.delete_database(app.db_path)
        logging.info("Closing FastAPI app.")
    
  
# Initialize the FastAPI app with lifespan
# This function will run when the app starts and stops
app = NoteSummarizerFastAPI(config_path=CONFIG_PATH, lifespan=lifespan)

# Initialize Jinja2 templates and set the directory for templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
# Add the filter to Jinja2
templates.env.filters['datetimeformat'] = datetimeformat

@app.get("/")
def read_root():
    return {"message": f"Welcome to {app.title}!"}

@app.get("/ingest")
def ingest_database():
    """Endpoint to initialize the database."""
    return ns_utils.initialize_database(db_path=app.db_path, data_dir=app.data_dir)

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
#     "template_id": "allergies",
#     "prompt: "Generate a note summary for the patient." (optional, used for custom templates)
# }

class PatientInfo(BaseModel):
    first_name: str = Field(..., description="The first name of the patient")
    last_name: str = Field(..., description="The last name of the patient")

class RequestBody(BaseModel):
    patient_info: PatientInfo
    template_id: str
    prompt: str | None = None 

@app.get("/answer", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "response": None})

@app.post("/answer")
async def answer_question(
        request_body: RequestBody = Body(..., description="Request body containing patient info, template id, and optional custom prompt."),
        response_type: str = Query("html", description="Response type: 'html' or 'json'")
    ):
    """Generate a patient summary using the template provided."""
    
    data = request_body.model_dump()
    logging.info(f"REQUEST RECEIVED: {data}")

    # Extract data from the request
    patient_info = data.get("patient_info", {})
    template_id = data.get("template_id", "")

    # Validate patient_info fields
    if not patient_info.get("first_name") or not patient_info.get("last_name"):
        logging.error("Invalid patient_info: Missing first_name or last_name.")
        response = {"error": "Invalid patient_info: Missing first_name or last_name."}
        return _generate_response(data, response, response_type)

    # Check if the template exists
    if template_id not in patient_templates:
        logging.error(f"Template '{template_id}' does not exist.")
        response = {"error": f"Template '{template_id}' does not exist."}
        return _generate_response(data, response, response_type)
    
    template = patient_templates[template_id].copy()

    # Custom template handling
    is_custom_prompt = False
    if template_id == "custom":
        is_custom_prompt = True
        # Check if the custom template is valid
        template["prompt"] = data.get("prompt", "")
        if not template["prompt"]:
            logging.error("Custom template requires a prompt.")
            response = {"error": "Custom template requires a prompt."}
            return _generate_response(data, response, response_type)
        
        logging.info(f"Custom Prompt: {template['prompt']}")

        try:
            template["sql_prompts"] = app.state.note_summarizer.generate_sql_prompts(template["prompt"], sql_templates)
        except Exception as e:
            logging.error(f"Error generating sql prompts list for the custom prompt: {e}")
            response = {"error": str(e)}
            return _generate_response(data, response, response_type)
        
        if not template["sql_prompts"]:
            logging.info("Insufficient information to answer the question.")
            response = {"info": "Insufficient information to answer the question."}
            return _generate_response(data, response, response_type)
  
    logging.info(f"Selected SQL prompts: {template['sql_prompts']}")
    template = ns_utils.populate_tempalate(template, is_custom_prompt=is_custom_prompt)

    try:
        response = ns_utils.generate_patient_summary(app.state.note_summarizer, patient_info=patient_info, template=template)
        logging.info(f"Summary generated successfully for template: {template_id}")
    except Exception as e:
        logging.error(f"Error generating summary for patient {patient_info}: {e}")
        response = {"error": str(e)}
        return _generate_response(data, response, response_type)
         
    # Render only the output section of the template
    return _generate_response(data, response, response_type, template["output_template"])

def _generate_response(request: Request, response: dict, response_type: str, output_template: str = None):
    """Helper function to generate the appropriate response based on response_type."""
    if response_type == "html":
        if output_template:
            return templates.TemplateResponse(output_template + ".html", {"request": request, "response": response})
        else:
            return templates.TemplateResponse("generic_output_template.html", {"request": request, "response": response})
    return JSONResponse(content=response)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()  # Raw request body (bytes)
    logging.error(f"Validation error.\n Request body: {body.decode('utf-8')}\n Validation issues: {exc.errors()}")
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": body.decode("utf-8")
        }
    )

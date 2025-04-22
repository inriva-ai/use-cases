# This module defines the template library for generating patient summaries and SQL queries.
# It includes a library of prompt templates for different sections of the summary and SQL queries to retrieve patient data.
# The templates are organized into sections and subsections, each with its own prompt template and SQL queries.
# The SQL queries are designed to retrieve specific information about the patient, such as demographics, conditions, allergies, encounters, medications, labs, imaging, insurance, hospitalizations, and polypharmacy.

#SQL queries templates to retrieve patient data
sql_templates = {
  "demographics_sql": "Retrieve all available demographic information for the patient {patient_details}.",
  "conditions_sql": "Retrieve all medical conditions (active and inactive) for the patient {patient_details}.",
  "allergies_sql": "Retrieve all recorded allergies and adverse reactions for the patient {patient_details}.",
  "encounters_sql": "Retrieve all hospital or facility visits associated with the patient {patient_details}, including facility details.",
  "medications_sql": "Retrieve all medications associated with the patient {patient_details}.",
  "labs_sql": "Retrieve all available lab results for the patient {patient_details}.",
  "imaging_sql": "Retrieve all imaging studies performed for the patient {patient_details}.",
  "insurance_sql": "Retrieve all insurance and payer information associated with the patient {patient_details}.",
  "hospitalizations_sql": "Retrieve all hospital visits for the patient {patient_details}.",
  "polypharmacy_sql": "Retrieve the total count of medications currently prescribed to the patient {patient_details}.",
  "immunizations_sql": "Retrieve ALL immunizations for the patient {patient_details}."
}

# User prompt templates for generating patient summaries
prompt_templates = {
    "demographics": "Summarize the patient's demographics, including name, date of birth, race, ethnicity, gender, top 3-5 active conditions, and any known allergies:",
    "visit_priorities": "Identify 3–5 top priorities for today's visit based on recent diagnoses, hospital visits, and medication changes. For each priority, provide associated action items:",
    "critical_changes": "List critical changes in the patient's condition since the last well visit, such as hospitalizations, new diagnoses, abnormal labs, or medication adjustments:",
    #"pending_items": "Summarize any pending labs, imaging, referrals, or insurance-related items that require follow-up:",
    #"risk_flags": "Highlight potential risk factors such as high fall risk, polypharmacy, hospice eligibility, or frequent hospitalizations:",
    "problem_list": "List all active medical conditions currently documented for the patient.\
                     For each medical condition, summarize relevant recent events, associated risks, coordination notes, pending items, and action items:",
    "admin_notes": "List administrative tasks (if any) requiring attention such as insurance changes or incomplete forms:",
    "medications": "Summarize the patient's current and past medications:",
    "symptoms": "Provide an overview of the patient's reported symptoms and their progression over time:",
    "physical_exam": "What are the key points and key notes/observations from the patient's last physical examination?",
    "consultation": "What are the key findings from the patient's last non well-visit consultation note?",
    "immunizations": "Summarize the patient's immunizations:",
    "allergies": "Highlight any noted allergies or adverse reactions documented in the patient's records."
}

default_output_schema = {
  "title": "generic_summary",
  "description": "Structured format for summarization. Output only information relevant to the prompt. Do not output unavailable information.",
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Title of the summary."
    },
    "abstract": {
      "type": "string",
      "description": "A brief summary of the key findings and conclusions."
    },
    "context": {
      "type": "string",
      "description": "Background information relevant to the summary."
    },
    "key_points": {
      "type": "array",
      "description": "List of main points covered in the summary.",
      "items": { "type": "string" }
    },
    "data": {
      "type": "array",
      "description": "Structured data relevant to the summary.",
      "items": {
        "type": "object",
        "properties": {
          "category": { "type": "string", "description": "Category of the data." },
          "details": { "type": "string", "description": "Details of the data entry." },
          "date": { "type": "string", "format": "date", "description": "Date of relevance." }
        }
      }
    },
    "analysis": {
      "type": "string",
      "description": "Interpretation and analysis of the summarized information."
    },
    "recommendations": {
      "type": "string",
      "description": "Recommendations based on the summary."
    },
    "conclusion": {
      "type": "string",
      "description": "Final summary of findings and next steps."
    }
  },
  "required": ["title", "abstract", "context", "key_points", "conclusion"]
}
# Reformatted output_templates to match the format of json_schema_client
output_schemas = {
    "demographics": {
        "title": "demographics_summary",
        "description": "Structured format for summarizing patient demographics.",
        "type": "object",
        "properties": {
            "name": { "type": "string", "description": "Patient's full name." },
            "dob": { "type": "string", "format": "date", "description": "Date of birth." },
            "race": { "type": "string", "description": "Patient's race." },
            "ethnicity": { "type": "string", "description": "Patient's ethnicity." },
            "gender": { "type": "string", "description": "Patient's gender." },
            "primary_conditions": { "type": "array", "items": { "type": "string" }, "description": "Top 3-5 active conditions." },
            "allergies": { "type": "array", "items": { "type": "string" }, "description": "Known allergies." }
        },
        "required": ["name", "dob"]
    },
    "visit_priorities": {
        "title": "visit_priorities",
        "description": "Structured format for identifying visit priorities with associated action items.",
        "type": "object",
        "properties": {
            "priorities": {
                "type": "array",
                "description": "List of visit priorities with associated action items.",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": { "type": "string", "description": "Name of the priority." },
                        "action_items": {
                            "type": "array",
                            "description": "List of action items associated with the priority.",
                            "items": { "type": "string" }
                        }
                    },
                    "required": ["name", "action_items"]
                }
            }
        },
        "required": ["priorities"]
    },
    "critical_changes": {
        "title": "critical_changes",
        "description": "Structured format for summarizing critical changes since the last well visit.",
        "type": "object",
        "properties": {
            "changes": {
                "type": "array",
                "items": { "type": "string" },
                "description": "List of all critical changes (hospitalizations, new diagnoses, abnormal labs, medication changes)."
            }
        },
        "required": ["changes"]
    },
    "active_problem_list": {
        "title": "active_problem_list",
        "description": "Structured format for listing medical conditions with detailed subsections.",
        "type": "object",
        "properties": {
            "problems": {
                "type": "array",
                "description": "List of problems with detailed information.",
                "items": {
                    "type": "object",
                    "properties": {
                        "condition_name": { "type": "string", "description": "Name of the medical condition." },
                        "recent_events": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "Relevant recent events such as hospitalizations, ER visits, or lab results."
                        },
                        "risks": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "Specific risks associated with the condition."
                        },
                        "coordination_notes": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "Notes on coordination with other providers or family."
                        },
                        "pending_items": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "Pending labs, tests, or referrals."
                        },
                        "suggested_actions": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "Recommended actions or to-dos for the condition."
                        }
                    },
                    "required": ["condition_name", "status"]
                }
            }
        },
        "required": ["problems"]
    },
    "admin_notes": {
        "title": "admin_notes",
        "description": "Structured format for listing administrative notes.",
        "type": "object",
        "properties": {
            "notes": {
                "type": "array",
                "items": { "type": "string" },
                "description": "List of all administrative concerns (insurance issues, documentation needs)."
            }
        },
        "required": ["notes"]
    },
    "medications": {
      "title": "medications_summary",
      "description": "Medications prescribed to the patient. Structured format for medical notes in research paper-like format. Output only information relevant to the prompt. Do not output unavailable information",   
      "type": "object",
      "properties": {
        "medications": {
        "description": "Medications prescribed to the patient.",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": { "type": "string", "description": "Name of the medication." },
                "dosage": { "type": "string", "description": "Dosage of the medication." },
                "frequency": { "type": "string", "description": "Frequency of administration." },
                "start_date": { "type": "string", "format": "date", "description": "Start date of the medication." },
                "end_date": { "type": ["string", "null"], "format": "date", "description": "End date of the medication, if applicable." }
            },
            "required": ["name", "dosage", "frequency", "start_date"]
        }
      },
      "notes": { "type": "string", "description": "Additional notes about medications." }
      },
      "required": ["notes"]
    },
   "default_output_schema": default_output_schema,
}

# Combine SQL templates, prompt templates, and structured output templates into a single library
patient_templates = {
    "patient_demographics": {
        "name": "Patient Demographics (*)",
        "prompt": "demographics",
        "sql_prompts": [
            "demographics_sql",
            "conditions_sql",
            "allergies_sql"
        ],
        "output_schema": "demographics",
        "output_template": "demographics"
    },
    "visit_priorities": {
        "name": "Visit Priorities (*)",
        "prompt": "visit_priorities",
        "sql_prompts": [
            "encounters_sql",
            "conditions_sql",
            "medications_sql"
        ],
        "output_schema": "visit_priorities",
        "output_template": "visit_priorities"
    },
    "critical_changes": {
        "name": "Critical Changes (*)",
        "prompt": "critical_changes",
        "sql_prompts": [
            "encounters_sql",
            "conditions_sql",
            "labs_sql",
            "medications_sql"
        ],
        "output_schema": "critical_changes",
        "output_template": "critical_changes"
    },
    "active_problem_list": {
        "name": "Active Problem List (*)",
        "prompt": "problem_list",
        "sql_prompts": [
            "conditions_sql"
        ],
        "output_schema": "active_problem_list",
        "output_template": "active_problem_list"
    },
    
    "administrative_notes": {
        "name": "Administrative Notes (*)",
        "prompt": "admin_notes",
        "sql_prompts": [
            "insurance_sql",
          ],
        "output_schema": "admin_notes",
        "output_template": "admin_notes"
    },
    "medications": {
        "name": "Medications (*)",
        "prompt": "medications",
        "sql_prompts": [
            "medications_sql",
        ],
        "output_schema": "medications",
        "output_template": "medications"
    },
    "symptoms": {
        "name": "Symptoms",
        "prompt": "symptoms",
        "sql_prompts": [
            "encounters_sql",
        ],
        "output_schema": "default_output_schema",
        "output_template": "default_output_template"
    },
    "physical_exam": {
        "name": "Physical Exam",
        "prompt": "physical_exam",
        "sql_prompts": [
            "encounters_sql",
        ],
        "output_schema": "default_output_schema",
        "output_template": "default_output_template"
    },
    "consultation": {
        "name": "Consultation",
        "prompt": "consultation",
        "sql_prompts": [
            "encounters_sql",
        ],
        "output_schema": "default_output_schema",
        "output_template": "default_output_template"
    },
    "immunizations": {
        "name": "Immunizations",
        "prompt": "immunizations",
        "sql_prompts": [
            "immunizations_sql",
        ],
        "output_schema": "default_output_schema",
        "output_template": "default_output_template"
    },
    "allergies": {
        "name": "Allergies",
        "prompt": "allergies",
        "sql_prompts": [
            "allergies_sql",
        ],
        "output_schema": "default_output_schema",
        "output_template": "default_output_template"
    }
}

# patient_templates = {
#     "medications": {
#         "name":  "medications",
#         "sql_prompt": "What medications are prescribed to the patient {patient_details}? Retrieve ALL medications for the patient.",
#         "prompt": "Summarize the patient's current medications:\n"

#     },
#     "symptoms": {
#         "name":  "encounters",
#         "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
#         "prompt": "Provide an overview of the patient's reported symptoms and their progression over time:\n"
#     },
#     "physical_exam": {
#         "name":  "physical_exam",
#         "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
#         "prompt": "What are the key points and key notes/observations from the patient's last physical examination?\n"
#     },
#     "consultation": {
#         "name":  "consultation",
#         "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
#         "prompt": "What are the key findings from the patient's last non well-visit consultation note?\n"
#     },
#     "immunizations": {
#         "name":  "immunizations",
#         "sql_prompt" : "Retrieve ALL immunizations for the patient {patient_details}.", 
#         "prompt": "Summarize the patient's immunizations:\n"
#     },
#     "allergies": {
#         "name":  "allergies",
#         "sql_prompt": "In a single query retrieve ALL noted allergies or adverse reactions information for the patient {patient_details}.",
#         "prompt": "Highlight any noted allergies or adverse reactions documented in the patient's records.\n"
#     },
# }
# #    "history": "Summarize the patient's medical history relevant to their current condition.",
# #    "chronic_conditions": "Highlight any chronic conditions and their management plans documented in the patient's history.",
# #    "procedures": "Summarize the patient's relevant procedures and surgeries.",
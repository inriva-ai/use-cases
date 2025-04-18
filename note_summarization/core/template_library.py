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
    "demographics_summary": "Summarize the patient's demographics, including name, date of birth, primary conditions, and any known allergies:",
    "visit_priorities": "Identify 3–5 top priorities for today's visit based on recent diagnoses, hospital visits, and medication changes:",
    "critical_changes": "List critical changes in the patient's condition in the last 30–60 days, such as hospitalizations, new diagnoses, abnormal labs, or medication adjustments:",
    "pending_items": "Summarize any pending labs, imaging, referrals, or insurance-related items that require follow-up:",
    "risk_flags": "Highlight potential risk factors such as high fall risk, polypharmacy, hospice eligibility, or frequent hospitalizations:",
    "problem_list": "List all medical conditions (active and inactive) currently documented for the patient:",
    "problem_detail": "For each medical condition, summarize relevant recent events, associated risks, coordination notes, pending items, and action items:",
    "admin_tasks": "List administrative tasks requiring attention such as insurance changes, incomplete forms, or facility concerns:",
    "medications_summary": "Summarize the patient's current and past medications:",
    "symptoms_summary": "Provide an overview of the patient's reported symptoms and their progression over time:",
    "physical_exam_summary": "What are the key points and key notes/observations from the patient's last physical examination?",
    "consultation_summary": "What are the key findings from the patient's last non well-visit consultation note?",
    "immunizations_summary": "Summarize the patient's immunizations:",
    "allergies_summary": "Highlight any noted allergies or adverse reactions documented in the patient's records."
}

# Reformatted output_templates to match the format of json_schema_client
output_schemas = {
    "demographics_summary": {
        "title": "demographics_summary",
        "description": "Structured format for summarizing patient demographics.",
        "type": "object",
        "properties": {
            "name": { "type": "string", "description": "Patient's full name." },
            "dob": { "type": "string", "format": "date", "description": "Date of birth." },
            "primary_conditions": { "type": "array", "items": { "type": "string" }, "description": "Primary medical conditions." },
            "allergies": { "type": "array", "items": { "type": "string" }, "description": "Known allergies." }
        },
        "required": ["name", "dob"]
    },
    "visit_priorities": {
        "title": "visit_priorities",
        "description": "Structured format for identifying visit priorities.",
        "type": "object",
        "properties": {
            "priority_1": { "type": "string", "description": "First priority for the visit." },
            "priority_2": { "type": "string", "description": "Second priority for the visit." },
            "priority_3": { "type": "string", "description": "Third priority for the visit." },
            "priority_4": { "type": "string", "description": "Fourth priority for the visit." },
            "priority_5": { "type": "string", "description": "Fifth priority for the visit." }
        },
        "required": ["priority_1"]
    },
    "critical_changes": {
        "title": "critical_changes",
        "description": "Structured format for summarizing critical changes since the last visit.",
        "type": "object",
        "properties": {
            "hospitalizations": { "type": "array", "items": { "type": "string" }, "description": "Recent hospitalizations." },
            "new_diagnoses": { "type": "array", "items": { "type": "string" }, "description": "New diagnoses." },
            "abnormal_labs": { "type": "array", "items": { "type": "string" }, "description": "Abnormal lab results." },
            "medication_changes": { "type": "array", "items": { "type": "string" }, "description": "Changes in medications." }
        },
        "required": ["hospitalizations", "new_diagnoses"]
    },
    "pending_items": {
        "title": "pending_items",
        "description": "Structured format for summarizing pending items.",
        "type": "object",
        "properties": {
            "pending_labs": { "type": "array", "items": { "type": "string" }, "description": "Pending lab results." },
            "pending_imaging": { "type": "array", "items": { "type": "string" }, "description": "Pending imaging studies." },
            "insurance_followups": { "type": "array", "items": { "type": "string" }, "description": "Insurance-related follow-ups." }
        },
        "required": ["pending_labs"]
    },
    "risk_flags": {
        "title": "risk_flags",
        "description": "Structured format for highlighting risk factors.",
        "type": "object",
        "properties": {
            "fall_risk": { "type": "boolean", "description": "High fall risk." },
            "polypharmacy": { "type": "boolean", "description": "Polypharmacy risk." },
            "hospice_eligibility": { "type": "boolean", "description": "Hospice eligibility." },
            "frequent_hospitalizations": { "type": "boolean", "description": "Frequent hospitalizations." }
        },
        "required": ["fall_risk"]
    },
    "problem_list": {
        "title": "problem_list",
        "description": "Structured format for listing medical conditions.",
        "type": "object",
        "properties": {
            "condition_name": { "type": "string", "description": "Name of the medical condition." },
            "status": { "type": "string", "description": "Status of the condition (active/inactive)." },
            "onset_date": { "type": "string", "format": "date", "description": "Date of onset." },
            "notes": { "type": "string", "description": "Additional notes about the condition." }
        },
        "required": ["condition_name", "status"]
    },
    "problem_detail": {
        "title": "problem_detail",
        "description": "Structured format for detailing medical conditions.",
        "type": "object",
        "properties": {
            "condition": { "type": "string", "description": "Name of the medical condition." },
            "events": { "type": "array", "items": { "type": "string" }, "description": "Relevant recent events." },
            "risks": { "type": "array", "items": { "type": "string" }, "description": "Associated risks." },
            "pending_items": { "type": "array", "items": { "type": "string" }, "description": "Pending items related to the condition." },
            "action_items": { "type": "array", "items": { "type": "string" }, "description": "Action items for the condition." }
        },
        "required": ["condition"]
    },
    "admin_tasks": {
        "title": "admin_tasks",
        "description": "Structured format for listing administrative tasks.",
        "type": "object",
        "properties": {
            "insurance_issues": { "type": "array", "items": { "type": "string" }, "description": "Insurance-related issues." },
            "facility_concerns": { "type": "array", "items": { "type": "string" }, "description": "Concerns related to facilities." },
            "documentation_needs": { "type": "array", "items": { "type": "string" }, "description": "Documentation needs." }
        },
        "required": ["insurance_issues"]
    },
    "medications_summary": {
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
    },
    "symptoms_summary": {
        "title": "symptoms_summary",
        "description": "Structured format for summarizing symptoms.",
        "type": "object",
        "properties": {
            "symptom_name": { "type": "string", "description": "Name of the symptom." },
            "onset_date": { "type": "string", "format": "date", "description": "Date of onset." },
            "progression": { "type": "string", "description": "Progression of the symptom over time." },
            "notes": { "type": "string", "description": "Additional notes about the symptom." }
        },
        "required": ["symptom_name", "onset_date"]
    },
    "physical_exam_summary": {
        "title": "physical_exam_summary",
        "description": "Structured format for summarizing physical exam findings.",
        "type": "object",
        "properties": {
            "exam_date": { "type": "string", "format": "date", "description": "Date of the physical exam." },
            "key_points": { "type": "array", "items": { "type": "string" }, "description": "Key points from the physical exam." },
            "notes": { "type": "string", "description": "Additional notes about the physical exam." }
        },
        "required": ["exam_date", "key_points"]
    },
    "consultation_summary": {
        "title": "consultation_summary",
        "description": "Structured format for summarizing consultation findings.",
        "type": "object",
        "properties": {
            "consultation_date": { "type": "string", "format": "date", "description": "Date of the consultation." },
            "key_findings": { "type": "array", "items": { "type": "string" }, "description": "Key findings from the consultation." },
            "notes": { "type": "string", "description": "Additional notes about the consultation." }
        },
        "required": ["consultation_date", "key_findings"]
    },
    "immunizations_summary": {
        "title": "immunizations_summary",
        "description": "Structured format for summarizing immunizations.",
        "type": "object",
        "properties": {
            "immunization_name": { "type": "string", "description": "Name of the immunization." },
            "date_administered": { "type": "string", "format": "date", "description": "Date the immunization was administered." },
            "notes": { "type": "string", "description": "Additional notes about the immunization." }
        },
        "required": ["immunization_name", "date_administered"]
    },
    "allergies_summary": {
        "title": "allergies_summary",
        "description": "Structured format for summarizing allergies.",
        "type": "object",
        "properties": {
            "allergy_name": { "type": "string", "description": "Name of the allergy." },
            "reaction": { "type": "string", "description": "Description of the reaction." },
            "notes": { "type": "string", "description": "Additional notes about the allergy." }
        },
        "required": ["allergy_name", "reaction"]
    }
}

# Combine SQL templates, prompt templates, and structured output templates into a single library
patient_templates = {
    "patient_demographics": {
        "name": "Patient Demographics",
        "prompt": "demographics_summary",
        "sql_prompts": [
            "demographics_sql",
            "conditions_sql",
            "allergies_sql"
        ],
        "output_schema": "demographics_summary",
        "user_output": "demographics_summary"
    },
    "visit_priorities": {
        "name": "Visit Priorities",
        "prompt": "visit_priorities",
        "sql_prompts": [
            "encounters_sql",
            "conditions_sql",
            "medications_sql"
        ],
        "output_schema": "visit_priorities",
        "user_output": "visit_priorities"
    },
    "critical_changes": {
        "name": "Critical Changes",
        "prompt": "critical_changes",
        "sql_prompts": [
            "encounters_sql",
            "conditions_sql",
            "labs_sql",
            "medications_sql"
        ],
        "output_schema": "critical_changes",
        "user_output": "critical_changes"
    },
    "pending_items": {
        "name": "Pending Items",
        "prompt": "pending_items",
        "sql_prompts": [
            "labs_sql",
            "imaging_sql",
            "insurance_sql"
        ],
        "output_schema": "pending_items",
        "user_output": "pending_items"
    },
    "risk_flags": {
        "name": "Risk Flags",
        "prompt": "risk_flags",
        "sql_prompts": [
            "hospitalizations_sql",
            "medications_sql"
        ],
        "output_schema": "risk_flags",
        "user_output": "risk_flags"
    },
    "active_problem_list": {
        "name": "Active Problem List",
        "prompt": "problem_list",
        "sql_prompts": [
            "conditions_sql"
        ],
        "output_schema": "problem_list",
        "user_output": "problem_list"
    },
    "problem_detail": {
        "name": "Problem Detail",
        "prompt": "problem_detail",
        "sql_prompts": [
            "conditions_sql",
            "encounters_sql",
            "labs_sql",
            "medications_sql",
            "insurance_sql"
        ],
        "output_schema": "problem_detail",
        "user_output": "problem_detail"
    },
    "administrative_overview": {
        "name": "Administrative Overview",
        "prompt": "admin_tasks",
        "sql_prompts": [
            "insurance_sql",
            "encounters_sql"
        ],
        "output_schema": "admin_tasks",
        "user_output": "admin_tasks"
    },
    "medications": {
        "name": "Medications",
        "prompt": "medications_summary",
        "sql_prompts": [
            "medications_sql"
        ],
        "output_schema": "medications_summary",
        "user_output": "medications_summary"
    },
    "symptoms": {
        "name": "Symptoms",
        "prompt": "symptoms_summary",
        "sql_prompts": [
            "encounters_sql"
        ],
        "output_schema": "symptoms_summary",
        "user_output": "symptoms_summary"
    },
    "physical_exam": {
        "name": "Physical Exam",
        "prompt": "physical_exam_summary",
        "sql_prompts": [
            "encounters_sql"
        ],
        "output_schema": "physical_exam_summary",
        "user_output": "physical_exam_summary"
    },
    "consultation": {
        "name": "Consultation",
        "prompt": "consultation_summary",
        "sql_prompts": [
            "encounters_sql"
        ],
        "output_schema": "consultation_summary",
        "user_output": "consultation_summary"
    },
    "immunizations": {
        "name": "Immunizations",
        "prompt": "immunizations_summary",
        "sql_prompts": [
            "immunizations_sql"
        ],
        "output_schema": "immunizations_summary",
        "user_output": "immunizations_summary"
    },
    "allergies": {
        "name": "Allergies",
        "prompt": "allergies_summary",
        "sql_prompts": [
            "allergies_sql"
        ],
        "output_schema": "allergies_summary",
        "user_output": "allergies_summary"
    }
}
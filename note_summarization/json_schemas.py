json_schema_client = {
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

json_schema_medical = {
    "title": "medical_note",
    "description": "Structured format for medical notes in research paper-like format. Output only information relevant to the prompt. Do not output unavailable information",
    "type": "object",
    "properties": {
        "title": {
        "type": "string",
        "description": "Title of the medical note."
        },
        "abstract": {
        "type": "string",
        "description": "A brief summary of the case, including key findings and conclusions."
        },
        "patient_details": {
        "type": "object",
        "description": "Demographic and basic patient information.",
        "properties": {
            "name": { "type": "string" },
            "age": { "type": "integer" },
            "dob": { "type": "string", "format": "date" },
            "gender": { "type": "string", "enum": ["Male", "Female", "Other"] },
            "date_of_visit": { "type": "string", "format": "date", 'description': "Today's date" }
        },
        "required": ["name", "age", "dob", "gender"]
        },
        "introduction": {
        "type": "string",
        "description": "Background information on the patient and presenting concerns."
        },
        "history_of_present_illness": {
        "type": "string",
        "description": "Detailed history of the patient's current symptoms and condition."
        },
        "past_medical_history": {
        "type": "array",
        "description": "List of past medical conditions, surgeries, or relevant history.",
        "items": { "type": "string" }
        },
        "medications": {
        "type": "array",
        "description": "Current medications prescribed to the patient.",
        "items": {
            "type": "object",
            "properties": {
            "name": { "type": "string" },
            "dosage": { "type": "string" },
            "frequency": { "type": "string" },
            "start_date": { "type": "string", "format": "date" },
            "end_date": { "type": ["string", "null"], "format": "date" }
            },
            "required": ["name", "dosage", "frequency", "start_date"]
        }
        },
        "symptoms": {
        "type": "array",
        "description": "List of reported symptoms.",
        "items": { "type": "string" }
        },
        "physical_examination": {
        "type": "string",
        "description": "Findings from the physical examination."
        },
        "diagnostic_tests": {
        "type": "array",
        "description": "List of diagnostic tests performed and results.",
        "items": {
            "type": "object",
            "properties": {
            "test_name": { "type": "string" },
            "result": { "type": "string" },
            "date": { "type": "string", "format": "date" }
            },
            "required": ["test_name", "result", "date"]
        }
        },
        "treatment_plan": {
        "type": "string",
        "description": "Planned or ongoing treatment for the patient."
        },
        "follow_up_recommendations": {
        "type": "string",
        "description": "Recommendations for follow-up visits or additional care."
        },
        "conclusion": {
        "type": "string",
        "description": "Final summary of findings, patient status, and next steps."
        }
    },
    "required": ["title", "abstract", "patient_details", "introduction", "conclusion"]
}

patient_templates = {
    "medications": {
        "name":  "medications",
        "sql_prompt": "What medications are prescribed to the patient {patient_details}? Retrieve ALL medications for the patient.",
        "prompt": "Summarize the patient's current medications:\n"

    },
    "symptoms": {
        "name":  "encounters",
        "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
        "prompt": "Provide an overview of the patient's reported symptoms and their progression over time:\n"
    },
    "physical_exam": {
        "name":  "physical_exam",
        "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
        "prompt": "What are the key points and key notes/observations from the patient's last physical examination?\n"
    },
    "consultation": {
        "name":  "consultation",
        "sql_prompt": "In a single query retrieve ALL encounters of the patient {patient_details} and for each encounter relevant conditions and observations.",
        "prompt": "What are the key findings from the patient's last non well-visit consultation note?\n"
    },
    "immunizations": {
        "name":  "immunizations",
        "sql_prompt" : "Retrieve ALL immunizations for the patient {patient_details}.", 
        "prompt": "Summarize the patient's immunizations:\n"
    },
    "allergies": {
        "name":  "allergies",
        "sql_prompt": "In a single query retrieve ALL noted allergies or adverse reactions information for the patient {patient_details}.",
        "prompt": "Highlight any noted allergies or adverse reactions documented in the patient's records.\n"
    },
}
#    "history": "Summarize the patient's medical history relevant to their current condition.",
#    "chronic_conditions": "Highlight any chronic conditions and their management plans documented in the patient's history.",
#    "procedures": "Summarize the patient's relevant procedures and surgeries.",
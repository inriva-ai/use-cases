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

json_schema_client = {
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

# Overview

This document provides an example that implements the [AI-Powered Clinical Summary Assistant](README.md) use case. 

Please note that the example implements only a subset of functional and technical requirements is intended for  demo purpose only.

# **Requriements**

## **Key Functional Requirements**

### **1. Medical Record Retrieval & Summarization**
- As a clinician, I should be able to access the medical records of a patient and receive an **AI-generated summary** answering predefined clinical questions:
    - Summarize the patient's recent lab results and highlight any abnormalities.
    - Provide an overview of the patient's reported symptoms and their progression over the last month.
    - What are the key points from the patient's last physical examination?
    - Highlight any noted allergies or adverse reactions documented in the patient's records.
    - Provide a timeline of the patient's major medical events and interventions.
    - Summarize the patient's family medical history pertinent to heart conditions.
    - What are the patient's previous surgical procedures and their outcomes?
    - Summarize the patient's immunization history and any upcoming due vaccines.


### **2. Interactive Querying**
- As a clinician, I should be able to **ask additional, patient-specific questions** and receive relevant, concise responses using online user interface.


## **Key Technical Requirements**

### **1. Retrieval-Augmented Generation (RAG) Framework**
- The solution should use a **RAG-based approach** to retrieve relevant medical records and generate accurate patient summaries. Specifically, RAG Haystack framework.

### **2. Data Source**
- The system must load relational patient data from a set of csv files. These files are 
    - observations.csv
    - organizations.csv
    - patients.csv
    - payer_transitions.csv
    - payers.csv
    - procedures.csv
    - providers.csv
    - supplies.csv
    - allergies.csv
    - careplans.csv
    - claims.csv
    - claims_transactions.csv
    - conditions.csv
    - devices.csv
    - encounters.csv
    - imaging_studies.csv
    - immunizations.csv
    - medications.csv

### **3. Vector Database for Chunking & Indexing**
- A **vector database** Milvus should be used to **efficiently retrieve relevant patient records**.

### **4. Tech Stack**
- The system should be implemented using **Python** and Haystack RAG framework 

### **5. User Interface**
- The user interface should be based on Langflow.

### **6. Model Support**
- The solution should allow running prompts against SaaS and locally hosted models.

### **7. Prompt Templates**
- The solution should support prompt templates.


# Architecture

The solution architecture focuses on two major pipeline:

- **Data Ingestion**: Processing CSV files, chunking data, embedding text, and storing it in a vector database.
- **Request Processing**: Retrieving relevant data, generating responses via LLMs, and presenting results through an interactive UI.


## 1. Architectural Components

### 1.1 Data Ingestion Pipeline
1. **CSV Data Loader**  
   - **Tool**: `pandas`  
   - **Reasoning**: Efficiently processes structured CSV data into DataFrames for further transformation.

2. **Text Preprocessing & Chunking**  
   - **Tool**: `LangChain DocumentLoaders`  
   - **Reasoning**: Handles chunking of text data for efficient embedding and retrieval.

3. **Text Embedding Model**  
   - **Tool**: `sentence-transformers` (e.g., `all-MiniLM-L6-v2`)  
   - **Reasoning**: Generates dense vector embeddings optimized for retrieval tasks.

4. **Vector Storage & Indexing**  
   - **Tool**: `Milvus`  
   - **Reasoning**: Optimized for scalable vector search, ensuring low-latency retrieval.

### 1.2 Request Processing Pipeline
1. **Query Interface (Interactive UI)**  
   - **Tool**: `Langflow`  
   - **Reasoning**: Provides a no-code/low-code environment for query construction and LLM interaction.

2. **Retrieval-Augmented Generation (RAG) Framework**  
   - **Tool**: `Haystack`  
   - **Reasoning**: Provides a structured pipeline for document retrieval and response generation.

3. **Retriever (Vector Search Engine)**  
   - **Tool**: `Milvus Retriever (Haystack)`  
   - **Reasoning**: Efficiently finds the most relevant chunks of medical data.

4. **Prompt Templates**  
   - **Tool**: `Jinja2`  
   - **Reasoning**: Enables structured prompt formatting for LLMs.

5. **LLM Integration**  
   - **Tools**: `OpenAI GPT-4` (for SaaS), `LLamaIndex` (for local models)  
   - **Reasoning**: Supports hybrid deployment models, allowing both cloud-based and on-prem inference.

6. **Response Generation & Summarization**  
   - **Tool**: `LangChain Prompt Templates`  
   - **Reasoning**: Ensures structured, template-based responses for consistent medical summaries.

---

## 2. Architectural Diagrams

### 2.1 Component View

The diagram below outlines the solution components grouped by pipeline.

```mermaid
graph TD;
    subgraph Data Ingestion
        A[CSV Loader] --> B[Text Chunking]
        B --> C[Embedding Model]
        C --> D[Vector Storage]
    end
    
    subgraph Query Processing
        E[User Query] --> F[Retriever]
        F --> G[Milvus Vector Search]
        G --> H[Prompt Construction]
        H --> I[LLM Inference]
        I --> J[Response Generation]
        J --> K[Final Output to UI]
    end
```

### 2.2 Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as Langflow UI
    participant Retriever as Haystack Retriever
    participant Milvus as Milvus Vector DB
    participant Prompt as Jinja2 Prompt Builder
    participant LLM as GPT-4 / LLamaIndex
    participant Output as Response Generator

    User->>UI: Enters query
    UI->>Retriever: Fetch relevant medical records
    Retriever->>Milvus: Search vector embeddings
    Milvus->>Retriever: Return relevant chunks
    Retriever->>Prompt: Format structured prompt
    Prompt->>LLM: Pass structured query
    LLM->>Output: Generate medical summary
    Output->>UI: Display structured response
```

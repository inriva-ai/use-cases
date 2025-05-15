# Setup Instructions for FastAPI Service and Langflow UI

This guide describes how to set up the FastAPI note summarization app and Langflow UI using direct installation, Docker, or Docker Compose.

---

## Option 1: Direct Installation

### FastAPI Service

1. Clone the repository:
   ```
   git clone https://github.com/inriva-ai/use-cases.git
   cd use-cases/note_summarization
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file by copying the example:
   ```
   cp .env.example .env
   ```

4. Add your API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

5. Start the FastAPI application:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8085
   ```

The FastAPI service will be available at http://localhost:8085

Once the FastAPI service is running, you can access the following FastAPI documentation endpoints in your browser:

- Swagger UI: http://localhost:8085/docs
- ReDoc: http://localhost:8085/redoc

### Langflow UI

1. Install Langflow:
   https://docs.langflow.org/get-started-installation

2. Create a `.langflow.env` file by copying the example:
   ```
   cd note_summarization/langflow
   cp .langflow.env.example .langflow.env
   ```

3. Add your API key to the `.langflow.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

4. Start the Langflow UI:
   ```
   langflow run --port 7860 --env-file .langflow.env
   ```

The Langflow UI will be available at http://localhost:7860

5. Upload `ns-langflow.json` by draggingand dropping it into the the main dashboard of the Langflow UI. 

6. In the Langflow UI, navigate to the Agent settings and select `OPENAI_API_KEY` as the OpenAI API Key. In Agent Instructions, set the DNS Name to `localhost`.

7. Run Agent component to run the flow with the default prompt (defined in User Question component). Go to the Playground to check the results.

---

## Option 2: Docker Installation

### FastAPI Service

1. Clone the repository:
   ```
   git clone https://github.com/inriva-ai/use-cases.git
   cd use-cases/note_summarization
   ```

2. Create a `.env` file by copying the example:
   ```
   cp .env.example .env
   ```

3. Add your API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Option A: Build the Docker image locally**
   ```
   docker build -t ghcr.io/inriva-ai/use-cases:latest .
   ```

5. **Option B: Use the prebuilt image from GitHub Container Registry**

   5.1 Authenticate with GitHub Container Registry if the image is private:
   ```
   echo YOUR_GITHUB_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
   ```
   Replace `YOUR_GITHUB_PAT` with your GitHub personal access token and `YOUR_GITHUB_USERNAME` with your GitHub username.

   5.2 Pull the latest image:
   ```
   docker pull ghcr.io/inriva-ai/use-cases:latest
   ```

6. Run the Docker container:
   ```
   docker run -d --name ns-fastapi-app --env-file .env -p 8085:8085 ghcr.io/inriva-ai/use-cases:latest
   ```

The FastAPI service will be available at http://localhost:8085

Once the FastAPI service is running, you can access the following FastAPI documentation endpoints in your browser:

- Swagger UI: http://localhost:8085/docs
- ReDoc: http://localhost:8085/redoc

### Langflow UI

1. Navigate to the `langflow` directory:
   ```
   cd langflow
   ```

2. Create a `.langflow.env` file by copying the example:
   ```
   cp .langflow.env.example .langflow.env
   ```

3. Add your API key to the `.langflow.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

4. Build the Docker image:
   ```
   docker build -t ghcr.io/inriva-ai/langflow-ns:latest .
   ```

5. Run the Docker container:
   ```
   docker run -d --name ns-langflow --env-file .langflow.env -p 7860:7860 --add-host=host.docker.internal:host-gateway ghcr.io/inriva-ai/langflow-ns:latest
   ```

The Langflow UI will be available at http://localhost:7860

6. In the Langflow UI, navigate to the Agent settings and select `OPENAI_API_KEY` as the OpenAI API Key. In Agent Instructions, set the DNS Name to `host.docker.internal`.

7. Run Agent component to run the flow with the default prompt (defined in User Question component). Go to the Playground to check the results.

---

## Option 3: Combined Installation Using Docker Compose

1. Clone the repository:
   ```
   git clone https://github.com/inriva-ai/use-cases.git
   cd use-cases/note_summarization
   ```

2. Create a `.env` file by copying the example:
   ```
   cp .env.example .env
   ```

3. Add your API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

4. Create a `.langflow.env` file in the `langflow` directory by copying the example:
   ```
   cd langflow
   cp .langflow.env.example .langflow.env
   ```

5. Add your API key to the `.langflow.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

6. Start the services using Docker Compose (from `use-cases/note_summarization` folder):
   ```
   docker-compose -f docker-compose-fastapi-langflow.yaml up -d
   ```

The FastAPI service will be available at http://localhost:8085

Once the FastAPI service is running, you can access the following FastAPI documentation endpoints in your browser:

- Swagger UI: http://localhost:8085/docs
- ReDoc: http://localhost:8085/redoc

Langflow UI will be available at http://localhost:7860

7. In the Langflow UI, navigate to the Agent settings and select `OPENAI_API_KEY` as the OpenAI API Key. In Agent Instructions, set the DNS Name to `ns-fastapi-app`.

8. Run Agent component to run the flow with the default prompt (defined in User Question component). Go to the Playground to check the results.



# Setup Instructions

This guide describes how to run the FastAPI note summarization app using Docker or a manual installation.

---

## Option 1: Run with Docker (build from source)

1. Clone the repository:

```
git clone https://github.com/inriva-ai/use-cases.git
cd use-cases/note_summarization
```

2. Create a `.env` file by copying the example:

```
cp .env.example .env
```

3. Build and run the Docker container:

```
docker-compose up -d --build
```

This will build the image using the Dockerfile and start the app in the background. The app will be available at http://localhost:8000.

---

## Option 2: Run with Docker (prebuilt image from GitHub Container Registry)

1. Authenticate with GitHub Container Registry if the image is private:

```
cd use-cases/note_summarization
echo YOUR_GITHUB_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

Replace `YOUR_GITHUB_PAT` with your GitHub personal access token and `YOUR_GITHUB_USERNAME` with your GitHub username.

2. Pull the latest image:

```
docker pull ghcr.io/inriva-ai/use-cases:latest
```

This ensures you are using the latest version of the prebuilt image.

3. Create a `.env` file by copying the example:

```
cp .env.example .env
```

4. Run the container:

```
docker run -it --env-file .env -p 8000:8000 ghcr.io/inriva-ai/use-cases:latest
```

The application will start and be accessible at http://localhost:8000.

---

## Option 3: Run locally without Docker

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

4. Start the FastAPI application:

```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application will be running locally and available at http://localhost:8000

## API Documentation

Once the application is running (in any mode), you can access the following documentation endpoints in your browser:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

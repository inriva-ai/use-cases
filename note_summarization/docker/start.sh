#!/bin/bash

cd /app

uvicorn main:app --host 0.0.0.0 --port 8000 &

exec bash
# This script starts the FastAPI server and then opens a bash shell.
# The FastAPI server will run in the background, and you can interact with it using curl or any HTTP client.
# The server will be accessible at http://localhost:8000.
# You can stop the server by terminating the bash shell or using Ctrl+C.
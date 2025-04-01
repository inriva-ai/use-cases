# Use an official Python image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the necessary files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY main.py summarizer.py json_schemas.py config.dev.yml /app/
COPY data/*  /app/data/

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
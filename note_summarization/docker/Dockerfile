# Use an official Python image
FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /app

# Copy the necessary files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/main.py .
COPY core/ ./core/
COPY config/ ./config/
COPY .env.example .
COPY data/ ./data/

# Copy and set permissions on the start script
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# Start the shell and FastAPI on container start
ENTRYPOINT ["/start.sh"]

# Expose the application port
EXPOSE 8000

# Run the application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
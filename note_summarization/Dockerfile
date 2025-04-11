# Use an official Python image
FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /src

# Copy the necessary files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ ./app/
COPY core/ ./core/
COPY config/ ./config/
COPY .env.example .
COPY data/ ./data/

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
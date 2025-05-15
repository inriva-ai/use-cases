# Base image with Langflow backend and frontend
FROM langflowai/langflow-backend:latest

# Create the folder for flows
RUN mkdir -p /app/flows

# Copy your flow file into the container
COPY ns-langflow.json /app/flows/

# Tell Langflow where to find the flow
ENV LANGFLOW_LOAD_FLOWS_PATH=/app/flows

# Expose the default Langflow port
EXPOSE 7860

# Co

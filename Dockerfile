FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen
# Install uvicorn explicitly
RUN pip install uvicorn[standard]
# Copy application code
COPY . .
# Create out directory if it doesn't exist
RUN mkdir -p out
# Expose port
EXPOSE 8000
# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

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
# Create startup script
RUN echo '#!/bin/bash\npython -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}' > /app/start.sh && chmod +x /app/start.sh
# Expose port
EXPOSE 8000
# Run the application
CMD ["/app/start.sh"]

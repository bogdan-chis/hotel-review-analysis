# Use a slim Python 3.11 base image to keep the image size small.
FROM python:3.11-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy and install dependencies first — Docker caches this layer separately
# so a code change won't force a full pip install on the next build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose the port uvicorn will listen on.
EXPOSE 8000

# Start the FastAPI app.
# --host 0.0.0.0 makes it reachable from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
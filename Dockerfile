# 1. Use a lightweight, official Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the grocery list and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all your awesome Python scripts into the container
COPY . .

# 5. Expose port 7860 (This is the mandatory port for Hugging Face Spaces)
EXPOSE 7860

# 6. The command to boot up your FastAPI server when the container starts
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
#Use the official Python 3.11 slim image as base
FROM python:3.11-slim

#Set the working directory inside the container
WORKDIR /app

#Copy requirements first (Docker caches this layer)
COPY requirements.txt .

#Install Python Dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Copy the rest of your code into the container
COPY . .

#Tell Docker which port the app uses
EXPOSE 8000

# The command that runs when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
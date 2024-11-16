FROM python:3.10.12

# Set a default value for PORT
ENV PORT=9003

# Create app directory
WORKDIR /app

# Copy only the necessary files and folders
COPY Procfile .
COPY clientApp.py .
COPY src/ src/
COPY templates/ templates/
COPY requirements.txt .

# Install dependencies
RUN pip3 install -r requirements.txt

# Use the PORT environment variable
EXPOSE $PORT

# Command to run the application
CMD gunicorn --workers=4 --bind 0.0.0.0:$PORT clientApp:app
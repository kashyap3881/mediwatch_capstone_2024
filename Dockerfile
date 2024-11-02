FROM python:3.10.12

# Set a default value for PORT
ENV PORT=9003

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

# Use the PORT environment variable
EXPOSE $PORT
CMD gunicorn --workers=4 --bind 0.0.0.0:$PORT clientApp:app
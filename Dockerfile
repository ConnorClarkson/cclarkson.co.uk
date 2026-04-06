# Use the official Python base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the required dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Expose the port on which the Flask app will run
EXPOSE 5001

# Set environment variables
ENV FLASK_APP=application.py

# Run via gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "application:application"]
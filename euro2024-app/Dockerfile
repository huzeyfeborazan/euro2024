FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Upgrade pip before installing any packages
RUN apt-get update && apt-get install -y gcc
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the application with Gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
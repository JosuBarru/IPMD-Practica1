# Use the alpine image
FROM python:3.9-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update packages
RUN apk update && \
    apk upgrade && \
    apk add --no-cache bash git openssh && \
    apk add --no-cache --virtual .build-deps build-base libffi-dev openssl-dev

# Install Python and other necessary packages
RUN apk add --no-cache python3 python3-dev \
    py-pip build-base libffi-dev openssl-dev

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY docker/* /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose port 80
EXPOSE 80

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:80", "main:app"]


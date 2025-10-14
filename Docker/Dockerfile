# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entire project to the working directory
# We copy requirements.txt first to leverage Docker layer caching
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir to reduce image size and a mirror for faster downloads
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy the rest of the application
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run api_server.py when the container launches
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
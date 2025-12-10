# Use Python 3.10 to match your development environment
FROM python:3.10

# Set working directory
WORKDIR /code

# Copy dependencies first for caching
COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code
COPY . /code

# Create cache directory for libraries that might need it
RUN mkdir -p /tmp/cache && chmod 777 /tmp/cache
ENV XDG_CACHE_HOME=/tmp/cache

# Expose port 7860 (Required by Hugging Face Spaces)
EXPOSE 7860

# Start the server on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
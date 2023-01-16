# Base Image
FROM python:3.10-slim

# Create working directory
WORKDIR /opt

# Copy dependencies and source code
COPY ["./", "./"]

# Install dependencies using the copied files
RUN pip install --upgrade -r requirements.txt

# Convert src to a package
RUN pip install -e .

# Entrypoint
CMD ["python", "./src/api/main.py", "--port", "8000", "--host", "0.0.0.0"]

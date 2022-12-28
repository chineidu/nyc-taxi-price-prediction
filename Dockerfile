# Base Image
FROM python:3.10-slim

# Create working directory
WORKDIR /opt

# Copy dependencies and source code
COPY ["./", "./"]

# Install dependencies using the copied files
RUN pip install --upgrade -r test_requirements.txt

# Convert src to a package
RUN python setup.py sdist && pip install -e .

# Entrypoint
CMD ["python", "./src/api/main.py"]

# Base Image
FROM python:3.10-slim

# Create working directory
WORKDIR /opt

# Copy dependencies and source code
COPY ["./", "./"]

# Install dependencies using the copied files
RUN pip install --upgrade -r test_requirements.txt \
    && pip-chill

RUN pip install --upgrade build && pip install -e .

# Entrypoint
CMD ["python", "./proj/src/api/main.py"]

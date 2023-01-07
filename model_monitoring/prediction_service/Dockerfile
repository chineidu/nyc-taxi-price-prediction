FROM python:3.10-slim

# Create working directory
WORKDIR /opt

# Copy all the requirements and source code
COPY ["./", "./"]

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


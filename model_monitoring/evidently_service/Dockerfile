FROM python:3.10-slim

# Create working directory
WORKDIR /opt

# Copy all the requirements and source code
COPY ["./", "./"]

RUN pip3 install --upgrade -r requirements.txt

CMD ["python", "app.py"]

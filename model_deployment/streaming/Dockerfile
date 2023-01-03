FROM public.ecr.aws/lambda/python:3.9

# Copy all the requirements and source code
COPY . .
RUN pip3 install --upgrade -r requirements.txt

# Set the CMD to your handler (could also be done as a 
# parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]

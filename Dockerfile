FROM public.ecr.aws/lambda/python:3.8

# Copy requirements
COPY requirements.txt .
RUN  pip3 install -r requirements.txt 

# Install the function's dependencies using file requirements.txt
# from your project folder.
COPY src/ .

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]

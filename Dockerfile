# Use an official Python runtime as the base image
#FROM python:3.10.0a6-buster
FROM python:3.8.5-buster

ADD Apps/Collection/src/api/file_request_handler.py .
ADD Apps/Collection/src/api .
#ENV PATH=$PATH:/home/max/Mountain_Stone_LLC/MntStn
#ENV PYTHONPATH /home/max/Mountain_Stone_LLC/MntStn
#THE ONLY PATH: print(os.environ.get('PYTHONPATH', '')) -> /Apps, maybe need more than just /Apps   ??!!?!!??!!?
# if <dest> ends with a trailing slash /, it will be considered a directory and the contents all directory will be copied
ENV PATH=$PATH:/Apps/
ENV PYTHONPATH /Apps/
ENV PYTHONPATH "${PYTHONPATH}:/Apps/Collection/src/api"
ENV PYTHONPATH "${PYTHONPATH}:Apps/Collection/src/api/file_request_handler.py"
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
# this fixed the error: "python: can't open file 'file_request.py': [Errno 2] No such file or directory"
# WORKDIR /Apps/Collection/src/api

# Copy the requirements file and install dependencies
COPY requirements.txt .


# Copy the rest of the application code into the container
COPY . .

COPY Apps/Collection/src/api ./Apps/Collection/src/api

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /


# Set the command to run your application
# try deleting this and runing the command manually in the container
#CMD ["python3", "./Apps/Collection/src/api/file_request.py"]

#weird double line in file output maybe problem??
#File "//Apps/Collection/src/api/file_request.py",
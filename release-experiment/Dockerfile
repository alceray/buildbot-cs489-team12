# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir requests scipy pandas numpy

# Make port 80 available to the world outside this container
EXPOSE 80

# Define arguments
ARG github_token
ARG repo_name
ARG release_notes_workflow_id
ARG release_workflow_id
ARG publish_release_workflow_id

# Define environment variable
ENV GITHUB_TOKEN $github_token
ENV REPO_NAME $repo_name
ENV RELEASE_NOTES_WORKFLOW_ID $release_notes_workflow_id
ENV RELEASE_WORKFLOW_ID $release_workflow_id
ENV PUBLISH_RELEASE_WORKFLOW_ID $publish_release_workflow_id

# Run script.py when the container launches
CMD ["python", "script.py"]

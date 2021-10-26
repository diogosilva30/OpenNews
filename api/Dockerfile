# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment varibles
# Dont store logs in buffers, send to console
ENV PYTHONUNBUFFERED 1  
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip install -r /code/requirements.txt

# Copy the current directory contents into the container at /code/
COPY . /code/
# Set the working directory to /code/
WORKDIR /code/

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "aautad.wsgi:application"]

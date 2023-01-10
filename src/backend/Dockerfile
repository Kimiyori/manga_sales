# syntax=docker/dockerfile:1
# Pull base image
FROM python:3.10
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set work directory
WORKDIR /aiohttp/src/backend
# Install dependencies
COPY Pipfile Pipfile.lock /aiohttp/src/backend/
RUN  pip install pipenv && pipenv install --system
# Copy project
COPY . /aiohttp/src/backend/
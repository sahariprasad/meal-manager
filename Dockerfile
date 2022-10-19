FROM python:3.10-slim-buster

WORKDIR /usr/src/app/meal-manager
# COPY . .
RUN pip install flask pymongo bcrypt
# RUN pip install pymongo
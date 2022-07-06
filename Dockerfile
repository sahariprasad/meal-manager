FROM python:3.10-slim-buster

WORKDIR /usr/src/app
COPY . .
RUN pip install flask
CMD ["python", "./meal-manager.py"]
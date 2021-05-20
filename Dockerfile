FROM python:3.8.0

# Exploit build cache
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENV FLASK_APP=src/app.py

CMD flask run --host="0.0.0.0" --port=80

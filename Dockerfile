FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY .chainlit/ chainlit/


CMD ["chainlit", "run", "cibbot.py", "--host", "0.0.0.0", "--port", "8000"]

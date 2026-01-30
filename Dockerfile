FROM python:3.11-slim

WORKDIR /app

COPY demo-app/simple-chat/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY demo-app/simple-chat/ .

EXPOSE 5000

CMD ["python", "app.py"]
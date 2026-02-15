FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create log directory
RUN mkdir -p /app/logs

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]

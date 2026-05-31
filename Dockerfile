FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app:app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Override in compose for --debug (auto-reload when code is bind-mounted)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

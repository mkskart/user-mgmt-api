FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg2
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY backend ./backend
COPY backend/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "-m", "backend.app.main"]
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    exiftool \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
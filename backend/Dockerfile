FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies if needed (e.g. for PyMuPDF/cffi)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh && \
    adduser --disabled-password --gecos "" appuser && \
    mkdir -p /data/uploads && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /data

USER appuser

EXPOSE 8000

CMD ["bash", "./start.sh"]

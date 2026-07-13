FROM python:3.10-slim

WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# INCREASE TIMEOUT to 1000 seconds and use a faster mirror (PyPI default is fine)
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

COPY . .

CMD ["python", "main.py"]

FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    ca-certificates \
    openssl \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*


COPY req.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r req.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
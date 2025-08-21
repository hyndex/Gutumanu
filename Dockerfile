# syntax=docker/dockerfile:1
FROM python:3.11-slim@sha256:8df0e8faf75b3c17ac33dc90d76787bbbcae142679e11da8c6f16afae5605ea7

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONHASHSEED=0

WORKDIR /app

COPY requirements.txt .
RUN pip install --require-hashes -r requirements.txt

COPY . .

CMD ["gunicorn", "gutumanu.wsgi:application", "--bind", "0.0.0.0:8000"]

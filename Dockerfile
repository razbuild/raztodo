FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV RAZTODO_DB=/data/tasks.db

WORKDIR /app

RUN pip install --no-cache-dir raztodo

VOLUME ["/data"]

ENTRYPOINT ["sh", "-c", "rt \"$@\"", "--"]
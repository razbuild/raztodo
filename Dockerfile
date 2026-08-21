FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ARG USER_UID=1000
ARG USER_GID=1000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV RAZTODO_DB=/data/tasks.db
ENV RAZTODO_WEB_HOST=0.0.0.0
ENV RAZTODO_WEB_PORT=8000
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY . /app

# Install from source with uv.lock (reproducible); --no-editable = clean installation
RUN uv sync --frozen --no-dev --no-editable --extra all

# Non-root user; build with --build-arg USER_UID=$(id -u) to match host ownership
RUN groupadd --gid "$USER_GID" raztodo \
    && useradd --uid "$USER_UID" --gid "$USER_GID" --create-home --shell /usr/sbin/nologin raztodo

# /data must be owned by the non-root user so named volumes inherit correct ownership
RUN mkdir -p /data \
    && chown -R "$USER_UID":"$USER_GID" /data

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

VOLUME ["/data"]
EXPOSE 8000

USER raztodo

ENTRYPOINT ["docker-entrypoint.sh"]
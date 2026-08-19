FROM python:3.9-slim

WORKDIR /app

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

VOLUME /app/data

EXPOSE 5000

ENTRYPOINT ["python", "-m", "raztodo.cli"]
CMD ["--help"]
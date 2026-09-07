# python:3.8 is past EOL, and there's no USER so this runs as root.
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py legacy_unused.py ./

ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]

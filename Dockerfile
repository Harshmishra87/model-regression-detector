FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY prompts/ prompts/
COPY data/ data/
COPY templates/ templates/
RUN mkdir -p results

CMD ["python", "-m", "src.main"]
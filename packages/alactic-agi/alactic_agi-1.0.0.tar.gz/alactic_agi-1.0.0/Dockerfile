FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY crawler/ crawler/
COPY indexer/ indexer/
COPY data/ data/
COPY alactic_framework.py .

RUN touch data/samples/output.json
RUN touch data/samples/output_clean.jsonl

EXPOSE 5000

CMD ["python", "alactic_framework.py"]
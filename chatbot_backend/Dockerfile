FROM python:3.11-slim

WORKDIR /code

COPY requirements.* ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip uninstall -y pinecone-plugin-inference

COPY . .

ENV PYTHONPATH=/code
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

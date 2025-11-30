FROM python:3.13-slim
WORKDIR /app

COPY requirements.txt .

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install --upgrade certifi requests urllib3 \
 && pip install --no-cache-dir -r requirements.txt

ENV GOOGLE_GENAI_USE_VERTEXAI=False

COPY . .

EXPOSE 8002

CMD ["sh", "-c", "uvicorn agent:a2a_app --host 0.0.0.0 --port 8002"]
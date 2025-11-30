FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs


WORKDIR /app

# ENV GOOGLE_API_KEY=AIzaSyB0qgtNswmSOrTKMtcsn3t7rwUxUsz0uYQ
ENV GOOGLE_GENAI_USE_VERTEXAI=False

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8003

CMD ["sh", "-c", "uvicorn agent:a2a_app --host 0.0.0.0 --port 8003"]
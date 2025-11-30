FROM python:3.13-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ENV GOOGLE_API_KEY=AIzaSyB0qgtNswmSOrTKMtcsn3t7rwUxUsz0uYQ
ENV GOOGLE_GENAI_USE_VERTEXAI=False

COPY . .

EXPOSE 8001

CMD ["sh", "-c", "uvicorn agent:a2a_app --host 0.0.0.0 --port 8001"]
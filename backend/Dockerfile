FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-21-jre-headless curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/lib && curl -fsSL https://repo.maven.apache.org/maven2/com/h2database/h2/2.3.232/h2-2.3.232.jar -o /app/lib/h2.jar
COPY app ./app
COPY migrations ./migrations
ENV H2_JAR_PATH=/app/lib/h2.jar
ENV H2_JDBC_URL=jdbc:h2:tcp://database:9092/./emsdb
ENV CORS_ORIGINS=http://localhost:4200
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

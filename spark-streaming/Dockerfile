FROM python:3.11-slim

WORKDIR /app

# Install Java 21 (available in Debian trixie)
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-21-jre-headless procps \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

CMD ["python", "streaming_job.py"]
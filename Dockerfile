FROM ollama/ollama:latest

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir runpod requests

# Copy application files
COPY handler.py /app/handler.py
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

WORKDIR /app

# Environment variables
ENV DEFAULT_MODEL=llama3.2:3b
ENV DEFAULT_VISION_MODEL=llama3.2-vision
ENV DEFAULT_TEMPERATURE=0.7
ENV DEFAULT_MAX_TOKENS=512
ENV OLLAMA_HOST=http://localhost:11434

# Override base image entrypoint
ENTRYPOINT []
CMD ["./start.sh"]

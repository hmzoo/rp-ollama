FROM ollama/ollama:latest

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY handler.py .
COPY start.sh .
RUN chmod +x start.sh

# Environment variables with defaults
ENV DEFAULT_MODEL=llama3.2:3b
ENV DEFAULT_VISION_MODEL=llama3.2-vision
ENV DEFAULT_TEMPERATURE=0.7
ENV DEFAULT_MAX_TOKENS=512
ENV OLLAMA_HOST=http://localhost:11434

# Expose Ollama port (optional, for debugging)
EXPOSE 11434

CMD ["./start.sh"]

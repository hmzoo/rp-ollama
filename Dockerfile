FROM runpod/base:0.6.2-cuda12.2.0

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Install Python dependencies
RUN pip install runpod requests

# Copy application files
WORKDIR /app
COPY handler.py .
COPY start.sh .
RUN chmod +x start.sh

# Environment variables
ENV DEFAULT_TEMPERATURE=0.7
ENV DEFAULT_MAX_TOKENS=512
ENV OLLAMA_HOST=http://localhost:11434

# Store Ollama models in the persistent volume
ENV OLLAMA_MODELS=/runpod-volume/models

CMD ["./start.sh"]

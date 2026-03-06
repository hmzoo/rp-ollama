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
ENV DEFAULT_MODEL=llama3.2:3b
ENV DEFAULT_VISION_MODEL=llama3.2-vision
ENV DEFAULT_TEMPERATURE=0.7
ENV DEFAULT_MAX_TOKENS=512
ENV OLLAMA_HOST=http://localhost:11434

CMD ["./start.sh"]

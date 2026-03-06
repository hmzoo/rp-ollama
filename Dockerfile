FROM runpod/pylang:3.11-1.54.0

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

COPY . /runpod/
RUN pip install -r /runpod/requirements.txt

WORKDIR /runpod
CMD ollama serve

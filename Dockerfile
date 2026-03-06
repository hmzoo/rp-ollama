FROM runpod/pylang:3.11-1.54.0

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copier les fichiers
COPY . /runpod/
WORKDIR /runpod

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Variable d'environnement pour le modèle par défaut
ENV DEFAULT_MODEL=llama3.2:3b
ENV DEFAULT_TEMPERATURE=0.7
ENV DEFAULT_MAX_TOKENS=512
ENV OLLAMA_HOST=http://localhost:11434

# Script de démarrage
COPY start.sh /runpod/start.sh
RUN chmod +x /runpod/start.sh

CMD ["/runpod/start.sh"]

#!/bin/bash
set -e

echo "🧹 Cleanup old containers..."
docker rm -f rp-ollama-test 2>/dev/null || true

echo "🔨 Building Docker image..."
docker build -t rp-ollama:test .

echo "🚀 Starting container with tinyllama (for quick testing)..."
docker run -d \
  --name rp-ollama-test \
  -e DEFAULT_MODEL=tinyllama \
  -e RUNPOD_API_KEY=test_key_local \
  -p 11434:11434 \
  rp-ollama:test

echo "⏳ Waiting for Ollama and model download..."
sleep 15

echo "📋 Container logs:"
docker logs rp-ollama-test 2>&1 | tail -40

echo ""
echo "✅ Test completed!"
echo ""
echo "To test with a better model (llama3.2:3b), run:"
echo "  docker run -d --name rp-ollama-test -e DEFAULT_MODEL=llama3.2:3b -e RUNPOD_API_KEY=test_key_local -p 11434:11434 rp-ollama:test"

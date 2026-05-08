#!/bin/sh
# Start the Ollama server in the background so we can use the CLI to pull the model.
ollama serve &
OLLAMA_PID=$!

# Wait until the server is accepting connections before pulling.
echo "Waiting for Ollama server to start..."
until ollama list > /dev/null 2>&1; do
  sleep 1
done

echo "Pulling model llama3.2:1b (this may take a few minutes on first run)..."
ollama pull llama3.2:1b

echo "Model ready. Ollama is running."

# Keep the server process in the foreground so the container stays alive.
wait $OLLAMA_PID
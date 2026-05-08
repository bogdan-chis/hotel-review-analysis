# Review Intelligence System

The Review Intelligence System is a full-stack application that analyzes hotel customer reviews using a local Large Language Model (llama3.2:1b via Ollama). It extracts key highlights and pain points from raw text and uses semantic embeddings to deduplicate and count recurring feedback.

## Prerequisites

* **Docker** and **Docker Compose** (for the backend and Ollama)
* **Node.js** and **npm** (for the React frontend)

## 1. Backend Setup (Docker)

The backend and the local LLM run entirely inside Docker containers.

A. **Configure Environment Variables:**
Navigate to the `backend/` directory (if applicable) or the project root, and copy the example environment file:

```bash
cp .env.example .env

```

Ensure `OLLAMA_HOST=http://ollama:11434` is set in your `.env` file so the FastAPI container can securely communicate with the Ollama container.

B. **Start the Services:**
Run the following command from the directory containing your `docker-compose.yml`:
```bash
docker compose up --build

```


*Note: On the very first run, the `ollama-entrypoint.sh` script will automatically download the `llama3.2:1b` model. This might take a minute or two depending on your internet connection. Subsequent startups will be much faster.*

The API will now be available at `http://localhost:8000`.

## 2. Frontend Setup (Local)

The frontend is a lightweight React + Vite application that runs locally on your host machine to make development fast and avoid unnecessary Docker container rebuilds.

1. **Navigate to the frontend directory:**
```bash
cd frontend

```


2. **Install Dependencies:**
```bash
npm install

```


3. **Start the Development Server:**
```bash
npm run dev

```



The frontend interface will be instantly accessible at `http://localhost:5173`.

## Usage

1. Open your browser and go to `http://localhost:5173`.
2. Prepare a `.txt` file containing your raw hotel reviews (one review per line).
3. Drag and drop your `.txt` file into the upload zone.
4. Click **Analyze Guest Feedback**.
5. Wait for the LLM pipeline to process, embed, and deduplicate your reviews. The structured results will automatically populate on the screen!

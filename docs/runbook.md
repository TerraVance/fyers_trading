# Consistent Trading Platform - Setup & Runbook

This guide walks you through setting up and running the Consistent Trading Platform, covering the database, backend, frontend, authentication, caching, and other visible services.

## 1. Prerequisites
Ensure you have the following installed on your machine:
*   **Docker & Docker Compose**: For running the PostgreSQL database and Adminer.
*   **Python (3.10+)**: For the FastAPI backend engine.
*   **Node.js (18+)**: For the React/Vite frontend.

---

## 2. Authentication & Environment Config (`Auth`)
The platform uses an environment variables file to manage API credentials and safety switches.

1.  Navigate to the root directory.
2.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
3.  Open `.env` and fill in your credentials:
    *   **Fyers API Credentials**: Provide `FYERS_APP_ID`, `FYERS_SECRET_KEY`, and `FYERS_REDIRECT_URI` to authenticate with the broker. (Note: While the README mentions Alice Blue, the current `.env` configuration targets Fyers).
    *   **OpenAI API Key**: Used for potential AI-assisted strategy generation.
    *   **Safety Switch**: Ensure `LIVE_ARMED=false` while testing to prevent real-money orders. Set to `true` only when you are ready to fire actual orders to the broker.

---

## 3. Database
The project uses PostgreSQL, which is containerized for easy setup.

1.  From the project root, start the database service:
    ```bash
    docker-compose up -d
    ```
2.  This command spins up two services:
    *   **PostgreSQL**: Running on port `5433` (mapped to internal `5432`). Credentials are user: `admin`, password: `secretpassword`, database: `consistent`.
    *   **Adminer**: A lightweight database management UI running on port `8080`.

---

## 4. Backend (Python/FastAPI)
The backend engine handles the trading logic, database interaction, and broker communication.

1.  Create and activate a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run Database Migrations**: Apply the initial database schema using Alembic:
    ```bash
    alembic upgrade head
    ```
4.  **Start the Server**:
    ```bash
    uvicorn backend.app.main:app --reload
    ```
    The API will now be running at `http://127.0.0.1:8000`. You can access the API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

---

## 5. Frontend (React/Vite)
The frontend provides the graphical user interface for the platform.

1.  Open a new terminal window and navigate to the frontend folder:
    ```bash
    cd frontend
    ```
2.  Install the Node packages:
    ```bash
    npm install
    ```
3.  **Start the Development Server**:
    ```bash
    npm run dev
    ```
    The application UI will now be accessible in your browser, typically at `http://localhost:5173`.

---

## 6. Local Data Caching (`Cache`)
To avoid rate limits and speed up backtesting, historical market data is cached locally.
*   **Directory**: The cache lives in `/backend/data_cache/`.
*   **Manifest Index**: A file named `manifest.json` tracks exactly what data (symbols, timeframes, date ranges) is currently stored on disk.
*   **Usage**: When you request data in the UI (via the Data Center page) or start a backtest, the backend first checks `manifest.json`. If the data exists locally, it loads it instantly. Otherwise, it downloads it via the broker API and saves it to the cache.

---

## 7. Additional Tools & Configurations
Other components visible to you that help manage the platform:

*   **Watchlist Configuration (`config/watchlist.yaml`)**: Edit this YAML file to change the default universe of trading symbols the system tracks. The backend parses this file on startup.
*   **Adminer UI**: While the database is running via Docker, you can visit `http://localhost:8080` in your browser. Select "PostgreSQL", enter the credentials from your `docker-compose.yml` (`server: db`, `username: admin`, `password: secretpassword`, `database: consistent`), and you can manually inspect your `orders`, `live_sessions`, and `backtest_runs` tables.

# Consistent Trading Platform - Project Structure

This document outlines the purpose, working, and existence of every directory and file in the Consistent Trading Platform repository.

## 1. Root Level Files

*   **`README.md`**: Contains the project description, setup instructions, and a checklist of project phases. It exists to provide new developers with a quick onboarding guide.
*   **`docker-compose.yml`**: Defines Docker services for local development, specifically a PostgreSQL database and an Adminer UI. It exists to standardize the database environment across different machines.
*   **`requirements.txt`**: Lists all Python packages (FastAPI, SQLAlchemy, etc.) required for the backend. It exists so the environment can be easily replicated using `pip install -r requirements.txt`.
*   **`alembic.ini`**: Configuration file for Alembic (the database migration tool). It exists to tell Alembic how to connect to the database and where to find migration scripts.

## 2. `/alembic/` (Database Migrations)
This directory manages schema changes for the PostgreSQL database.

*   **`README`**: Standard Alembic placeholder explaining the directory.
*   **`env.py`**: A Python script run whenever Alembic is invoked. It exists to set up the SQLAlchemy engine and connect the application's models (`Base.metadata`) so Alembic can auto-generate migrations.
*   **`script.py.mako`**: A template file used by Alembic to generate new migration scripts.
*   **`/versions/7e6d109f1e92_initial_schema.py`**: The initial migration script. It exists to create the `backtest_runs`, `live_sessions`, and `orders` tables in a fresh database.

## 3. `/config/`
*   **`watchlist.yaml`**: A YAML file containing a list of trading symbols (e.g., NIFTY, BANKNIFTY) to track or fetch data for. It exists to allow users to configure their universe of assets without changing code.

## 4. `/documents/`
*   **`alice_blue_trading_b4891700.plan.md`**: An artifact/plan document likely generated during previous AI coding sessions outlining the implementation of the broker adapter.

## 5. `/backend/` (FastAPI Application)
This directory houses the entire Python trading engine and API.

### Core App Setup
*   **`app/main.py`**: The entry point for the FastAPI server. It initializes the app, configures CORS, handles global exceptions, sets up logging, mounts all REST API routers, and exposes the WebSocket endpoint (`/ws/v1/stream`) for real-time frontend updates.

### `/backend/app/api/` (API Layer)
These files expose REST endpoints and WebSockets for the frontend to interact with.
*   **`routers/backtests.py`**: Endpoints to start, stop, and list backtests.
*   **`routers/broker.py`**: Endpoints to manage the connection to the Alice Blue broker (login, check status).
*   **`routers/config.py`**: Endpoints to fetch or update application configurations (like API keys).
*   **`routers/data.py`**: Endpoints to trigger historical data downloads and manage the local data cache.
*   **`routers/health.py`**: A simple `/health` endpoint to check if the API is alive.
*   **`routers/live.py`**: Endpoints to manage real-money live trading sessions.
*   **`routers/paper.py`**: Endpoints to manage paper (simulated) trading sessions.
*   **`routers/risk.py`**: Endpoints to configure and fetch risk management rules (max drawdown, max loss per day).
*   **`routers/strategy.py`**: Endpoints to list available strategies and their parameters.
*   **`ws/manager.py`**: Manages active WebSocket connections to push live data (ticks, PNL updates, order statuses) to the frontend.

### `/backend/app/core/` (Domain Logic)
*   **`config.py`**: Loads and validates environment variables (like Database URLs and Broker API keys).
*   **`errors.py`**: Defines custom application exceptions (e.g., `AppError`) to standardize error responses sent to the client.
*   **`models.py`**: Defines all Pydantic schemas (e.g., `Bar`, `Position`, `Signal`, `Order`) used for data validation and business logic across the app.
*   **`engine/backtest.py`**: The core loop for backtesting. Simulates time progression by iterating over historical bars and feeding them to strategies.
*   **`engine/live.py`**: The core loop for live trading. Subscribes to real-time broker ticks and places actual orders.
*   **`engine/paper.py`**: The core loop for paper trading. Subscribes to real-time broker ticks but simulates order execution locally.
*   **`engine/risk_guard.py`**: A safety layer that intercepts order intents before they reach the broker, rejecting them if they violate predefined risk rules (e.g., exceeding daily loss limits).
*   **`strategy/base.py`**: The base `Strategy` class that all custom strategies must inherit from. Enforces the implementation of the `on_bar` or `on_tick` methods.
*   **`strategy/generator.py`**: Utility to dynamically load strategy classes or scaffold new strategy templates.

### `/backend/app/infrastructure/` (External Integrations)
*   **`broker/base.py`**: An abstract interface defining the methods any broker adapter must implement (e.g., `place_order`, `get_historical_data`).
*   **`broker/fake.py`**: A mock broker implementation used for testing and paper trading offline.
*   **`broker/fyers.py`**: The actual broker adapter that translates the platform's standard requests into broker-specific HTTP API calls.
*   **`data/cache.py`**: Manages the local storage of historical market data. Prevents repeatedly downloading the same data from the broker.
*   **`data/downloader.py`**: Coordinates fetching data from the broker and saving it to the cache via `cache.py`.
*   **`database/models.py`**: SQLAlchemy ORM classes that map directly to the PostgreSQL database tables.
*   **`database/repo.py`**: The Repository pattern implementation. Contains the SQL queries to read/write `BacktestRun`, `LiveSession`, and `Order` records.
*   **`database/session.py`**: Manages the database connection pool and provides a `get_db` dependency for FastAPI routes.

### `/backend/app/strategies/`
*   **`sma_momentum_strategy.py`**: An example strategy implementation using Simple Moving Averages. It exists to demonstrate how users can write their own logic.

### `/backend/app/utils/`
*   **`logger.py`**: Configures the Python logging format and levels.
*   **`rate_limiter.py`**: Implements logic to prevent exceeding the broker's API rate limits.
*   **`time_utils.py`**: Helper functions for dealing with market hours, converting timestamps, and handling timezones.
*   **`watchlist.py`**: Parses and loads the `config/watchlist.yaml` file into Python objects.

### `/backend/tests/` (Unit Tests)
*   `test_backtest.py`, `test_broker.py`, `test_data.py`, `test_db.py`, `test_health.py`, `test_shared.py`, `test_strategy.py`: Pytest files asserting that individual components of the backend function correctly. They exist to prevent regressions during development.

### `/backend/data_cache/`
*   **`manifest.json`**: An index of all locally cached historical data files. It exists so the app can quickly determine what data is available offline without scanning the filesystem.

---

## 6. `/frontend/` (React SPA)
This directory contains the user interface.

### Root Frontend Files
*   **`package.json` & `package-lock.json`**: Define npm dependencies (React, Vite, Tailwind/Recharts) and scripts.
*   **`vite.config.ts`**: Configuration for the Vite bundler (e.g., port settings, plugins).
*   **`index.html`**: The main HTML file where the compiled React app is injected.
*   **`tsconfig.*.json`**: TypeScript configuration files defining compiler rules for the frontend.
*   **`README.md`**: Standard Vite React setup guide.

### `/frontend/public/`
*   **`favicon.svg` & `icons.svg`**: Static assets served directly to the browser.

### `/frontend/src/` (Source Code)
*   **`main.tsx`**: The React entry point that renders the `<App />` into the DOM.
*   **`App.tsx`**: The main router component that maps URLs (e.g., `/backtest`) to specific Page components.
*   **`App.css` & `index.css`**: Global stylesheets defining base styles and utility classes.

#### `/frontend/src/assets/`
*   Contains image assets (`hero.png`, `react.svg`, `vite.svg`) imported directly into React components.

#### `/frontend/src/layouts/`
*   **`AppLayout.tsx`**: A wrapper component that provides the consistent shell of the app (like the navigation sidebar/header) around the varying page content.

#### `/frontend/src/pages/`
These are the top-level views for the different tabs in the application.
*   **`BrokerPage.tsx`**: UI to input API credentials and view connection status.
*   **`DataCenterPage.tsx`**: UI to view cached data, manage the watchlist, and trigger historical downloads.
*   **`StrategyLabPage.tsx`**: UI to browse, edit, or configure trading strategies.
*   **`BacktestPage.tsx`**: UI to configure backtest parameters, run them, and view results (equity curves, trade tables).
*   **`PaperPage.tsx`**: UI to monitor active paper trading sessions and simulated PNL.
*   **`LivePage.tsx`**: UI to monitor real-money trading sessions, active positions, and real-time orders.

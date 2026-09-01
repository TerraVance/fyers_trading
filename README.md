# Consistent - Alice Blue Trading Platform

A local trading platform with backtesting and live order execution using the Alice Blue broker.

## Setup

1. **Backend (FastAPI)**
   ```bash
   # Create and activate virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the server
   uvicorn backend.app.main:app --reload
   ```

2. **Frontend (React + Vite)**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Configuration**
   Copy `.env.example` to `.env` and fill in your Alice Blue credentials.

## Features (In Progress)
- [x] Phase 1: Framework
- [x] Phase 2: Shared Components
- [x] Phase 3: Database
- [x] Phase 4: API Stubs
- [x] Phase 5: Broker Adapter
- [x] Phase 6: Cache with Manifest
- [x] Phase 7: Strategy Component
- [x] Phase 8: Backtest Engine
- [x] Phase 9: Dashboard Backtest
- [x] Phase 10: Live Engine Paper Mode
- [x] Phase 11: Risk Guard
- [x] Phase 12: Live Orders

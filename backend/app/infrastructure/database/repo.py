from sqlalchemy.orm import Session
from . import models as db_models
from backend.app.core.models import LiveSession, Order, BacktestRun
from typing import Optional, List

class RecordsRepo:
    def __init__(self, db: Session):
        self.db = db

    # --- Live Sessions ---
    def create_session(self, session_data: LiveSession) -> db_models.LiveSessionModel:
        db_session = db_models.LiveSessionModel(**session_data.model_dump(exclude={"id"}))
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return db_session

    def update_session_heartbeat(self, session_id: int, last_active_ms: int, state_file: str) -> Optional[db_models.LiveSessionModel]:
        db_session = self.db.query(db_models.LiveSessionModel).filter(db_models.LiveSessionModel.id == session_id).first()
        if db_session:
            db_session.last_active_ms = last_active_ms
            db_session.state_file = state_file
            self.db.commit()
            self.db.refresh(db_session)
        return db_session

    # --- Orders ---
    def insert_order(self, order_data: Order) -> db_models.OrderModel:
        db_order = db_models.OrderModel(**order_data.model_dump(exclude={"id"}))
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def get_order(self, order_id: int) -> Optional[db_models.OrderModel]:
        return self.db.query(db_models.OrderModel).filter(db_models.OrderModel.id == order_id).first()

    # --- Backtest Runs ---
    def save_backtest(self, run_data: BacktestRun) -> db_models.BacktestRunModel:
        db_run = db_models.BacktestRunModel(**run_data.model_dump(exclude={"id"}))
        self.db.add(db_run)
        self.db.commit()
        self.db.refresh(db_run)
        return db_run

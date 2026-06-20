from sqlmodel import SQLModel, create_engine
from app.core.config import Settings

_engine = None


def get_engine(settings: Settings):
    global _engine
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine


def _migrate_sqlite_schema(engine) -> None:
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as conn:
        rows = conn.exec_driver_sql("PRAGMA table_info(recipient)").fetchall()
        if not rows:
            return
        existing = {row[1] for row in rows}
        for column, column_type in (
            ("default_payout_asset", "VARCHAR(12)"),
            ("default_payout_amount", "FLOAT"),
            ("default_schedule_cadence", "VARCHAR(20)"),
            ("default_schedule_day", "VARCHAR(20)"),
        ):
            if column not in existing:
                conn.exec_driver_sql(f"ALTER TABLE recipient ADD COLUMN {column} {column_type}")


def create_db_and_tables(engine) -> None:
    SQLModel.metadata.create_all(engine)
    _migrate_sqlite_schema(engine)

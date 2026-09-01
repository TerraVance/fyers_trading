from datetime import datetime, timezone
import zoneinfo

IST = zoneinfo.ZoneInfo("Asia/Kolkata")

def now_ms_utc() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)

def ist_to_utc_ms(dt_ist: datetime) -> int:
    """Convert a naive datetime (assumed IST) or aware IST datetime to UTC ms."""
    if dt_ist.tzinfo is None:
        dt_ist = dt_ist.replace(tzinfo=IST)
    return int(dt_ist.astimezone(timezone.utc).timestamp() * 1000)

def utc_ms_to_ist(ts_ms: int) -> datetime:
    """Convert a UTC epoch ms to an aware datetime in IST."""
    dt_utc = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    return dt_utc.astimezone(IST)


from typing import List, Optional, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class TradeSchema(BaseModel):
    tradeId: str
    tenant: str
    audit: dict
    brokerRef: Optional[str] = None
    instrument: dict
    side: Literal["BUY", "SELL"]
    qty: int
    price: float
    fees: float = 0.0
    openTs: Optional[datetime] = None
    closeTs: Optional[datetime] = None
    status: Literal["OPEN", "CLOSED", "CANCELLED"]
    strategyTag: Optional[str] = None
    regimeTagIds: List[str] = []
    journalEntryIds: List[str] = []
    screenshotIds: List[str] = []
    realizedPnL: Optional[float] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}



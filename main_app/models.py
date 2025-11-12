from typing import Optional, List, Dict, Any, NewType
from datetime import datetime, date, timezone
from pydantic import BaseModel, Field, EmailStr
import os
from django.db import models
from django.contrib.auth.models import User
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic_mongo import AbstractRepository, PydanticObjectId

# Lazy MongoClient getter — don't import or connect at import time
_mongo_client = None
_mongo_client_class = None

def get_mongo_client(uri=None):
    global _mongo_client, _mongo_client_class
    if _mongo_client is None:
        if _mongo_client_class is None:
            try:
                from pymongo import MongoClient as MC
                _mongo_client_class = MC
            except ImportError:
                _mongo_client_class = None
                return None
        if _mongo_client_class is not None:
            import os
            uri = uri or os.environ.get('uri')
            _mongo_client = _mongo_client_class(uri)
    return _mongo_client


# Django Models
class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=16)
    side = models.CharField(max_length=4, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.side} {self.qty} {self.symbol} @ {self.price}"


# Replaced ObjectIdStr with PydanticObjectId
class TenantScoped(BaseModel):
    orgId: PydanticObjectId = Field(description="Tenant/org scope")
    userId: Optional[PydanticObjectId] = Field(None, description="Actor within tenant")

class AuditMeta(BaseModel):
    # MongoDB often manages creation timestamps, but we can keep this for explicit control.
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = None
    deletedAt: Optional[datetime] = None

# --- Users and auth ---

class UserSchema(BaseModel):
    # MongoDB documents implicitly have an `_id` field. We model it explicitly as `id` in pydantic-mongo.
    # The original models used fields like `userId`, `eventId` etc. We will map those to the `id` field
    # which the repository pattern expects for the primary key.
    id: PydanticObjectId = Field(alias="_id")
    orgId: PydanticObjectId
    email: EmailStr
    role: str = Field(pattern="^(admin|analyst|reader)$")
    mfaEnabled: bool = False
    preferences: Dict[str, Any] = {}

class UserRepository(AbstractRepository[UserSchema]):
    class Meta:
        collection_name = 'users'

# --- Trading Journal ---

class Instrument(BaseModel):
    underlying: str
    optionType: str = Field(pattern="^(CALL|PUT)$")
    strike: float
    expiry: date

class TradeSchema(BaseModel):
    # Mapping tradeId to the MongoDB document ID
    id: PydanticObjectId = Field(alias="_id")
    tenant: TenantScoped
    audit: AuditMeta
    brokerRef: Optional[str] = None
    instrument: Instrument
    side: str = Field(pattern="^(BUY|SELL)$")
    qty: int
    price: float
    fees: float = 0.0
    openTs: Optional[datetime] = None
    closeTs: Optional[datetime] = None
    status: str = Field(pattern="^(OPEN|CLOSED|CANCELLED)$")
    strategyTag: Optional[str] = None
    regimeTagIds: List[PydanticObjectId] = [] # Changed str to PydanticObjectId
    journalEntryIds: List[PydanticObjectId] = []
    screenshotIds: List[PydanticObjectId] = []
    realizedPnL: Optional[float] = None
    unrealizedPnL: Optional[float] = None

class TradeRepository(AbstractRepository[TradeSchema]):
    class Meta:
        collection_name = 'trades'

class ChecklistItem(BaseModel):
    label: str
    checked: bool = False

class JournalEntry(BaseModel):
    # Mapping entryId to the MongoDB document ID
    id: PydanticObjectId = Field(alias="_id")
    tenant: TenantScoped
    audit: AuditMeta
    tradeId: Optional[PydanticObjectId] = None
    setup: Optional[str] = None
    thesis: Optional[str] = None
    riskPlan: Optional[str] = None
    emotions: Optional[str] = None
    checklistItems: List[ChecklistItem] = []
    tags: List[str] = []
    screenshotIds: List[PydanticObjectId] = []

class JournalEntryRepository(AbstractRepository[JournalEntry]):
    class Meta:
        collection_name = 'journal_entries'

class NotebookNote(BaseModel):
    # Mapping noteId to the MongoDB document ID
    id: PydanticObjectId = Field(alias="_id")
    tenant: TenantScoped
    audit: AuditMeta
    title: str
    markdown: str
    backlinks: Dict[str, List[PydanticObjectId]] = Field(default_factory=dict)
    version: int = 1

class NotebookNoteRepository(AbstractRepository[NotebookNote]):
    class Meta:
        collection_name = 'notebook_notes'


# --- Market factors and analytics ---

class MarketFactorValues(BaseModel):
    VIX: Optional[float] = None
    breadth: Optional[float] = None
    trend: Optional[float] = None
    volRegime: Optional[str] = None
    liquidityProxy: Optional[float] = None

class MarketFactor(BaseModel):
    # Mapping factorId to the MongoDB document ID
    id: PydanticObjectId = Field(alias="_id")
    tenant: TenantScoped
    audit: AuditMeta
    date: date
    values: MarketFactorValues
    notes: Optional[str] = None
    tags: List[str] = []

class MarketFactorRepository(AbstractRepository[MarketFactor]):
    class Meta:
        collection_name = 'market_factors'


class AnalyticsMetrics(BaseModel):
    winRate: Optional[float] = None
    expectancy: Optional[float] = None
    drawdown: Optional[float] = None
    riskOfRuin: Optional[float] = None
    sharpeLike: Optional[float] = None
    mae: Optional[float] = None
    mfe: Optional[float] = None

class CohortView(BaseModel):
    byStrategy: Dict[str, AnalyticsMetrics] = {}
    byRegime: Dict[str, AnalyticsMetrics] = {}
    byTimeOfDay: Dict[str, AnalyticsMetrics] = {}

class AnalyticsSnapshot(BaseModel):
    # Mapping snapshotId to the MongoDB document ID
    id: PydanticObjectId = Field(alias="_id")
    tenant: TenantScoped
    audit: AuditMeta
    granularity: str = Field(pattern="^(daily|weekly|monthly)$")
    periodStart: date
    periodEnd: date
    metrics: AnalyticsMetrics
    cohorts: CohortView

class AnalyticsSnapshotRepository(AbstractRepository[AnalyticsSnapshot]):
    class Meta:
        collection_name = 'analytics_snapshots'


class Attachment(BaseModel):
    # Mapping fileId to the MongoDB document ID
    id: PydanticObjectId = Field(alias="_id")
    tenant: TenantScoped
    audit: AuditMeta
    type: str = Field(pattern="^(screenshot|csv)$")
    url: str
    checksum: str
    tradeId: Optional[PydanticObjectId] = None
    journalEntryId: Optional[PydanticObjectId] = None

class AttachmentRepository(AbstractRepository[Attachment]):
    class Meta:
        collection_name = 'attachments'

# --- Time tracking and habits ---

class BreakBlock(BaseModel):
    start: datetime
    end: datetime
    type: str = Field(pattern="^(break|lunch)$")

class RuleCheck(BaseModel):
    label: str
    checked: bool

class Session(BaseModel):
    # Mapping sessionId to the MongoDB document ID
    id: PydanticObjectId = Field(alias="_id")
    tenant: TenantScoped
    audit: AuditMeta
    type: str = Field(pattern="^(trading|research|review)$")
    clockIn: datetime
    clockOut: Optional[datetime] = None
    breaks: List[BreakBlock] = []
    lunch: Optional[BreakBlock] = None
    notes: Optional[str] = None
    ruleChecklist: List[RuleCheck] = []
    tags: List[str] = []
    adherenceScore: Optional[float] = None

class SessionRepository(AbstractRepository[Session]):
    class Meta:
        collection_name = 'sessions'

class BehaviorEvent(BaseModel):
    # Mapping eventId to the MongoDB document ID
    id: PydanticObjectId = Field(alias="_id")
    tenant: TenantScoped
    audit: AuditMeta
    timestamp: datetime
    type: str = Field(pattern="^(emotion|rule_violation|adherence)$")
    details: Dict[str, Any] = {}
    tradeId: Optional[PydanticObjectId] = None
    sessionId: Optional[PydanticObjectId] = None

class BehaviorEventRepository(AbstractRepository[BehaviorEvent]):
    class Meta:
        collection_name = 'behavior_events'

class ImportJob(BaseModel):
    # Mapping jobId to the MongoDB document ID
    id: PydanticObjectId = Field(alias="_id")
    tenant: TenantScoped
    audit: AuditMeta
    source: str
    mappingTemplateId: Optional[str] = None
    status: str = Field(pattern="^(PENDING|RUNNING|COMPLETED|FAILED)$")
    stats: Dict[str, int] = {}
    errors: List[Dict[str, Any]] = []

class ImportJobRepository(AbstractRepository[ImportJob]):
    class Meta:
        collection_name = 'import_jobs'


# Example Usage (assuming you have a MongoClient)
# client = MongoClient("mongodb://localhost:27017")
# db = client["your_database_name"]
# user_repo = UserRepository(database=db)

# new_user = UserSchema(orgId=PydanticObjectId(), email="test@example.com", role="admin")
# user_repo.save(new_user)
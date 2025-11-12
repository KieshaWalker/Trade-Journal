from typing import Optional, List, Dict, Any, NewType
from datetime import datetime, date, timezone
from pydantic import BaseModel, Field, EmailStr
import os
from django.db import models
from django.contrib.auth.models import User
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
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
            uri = uri or os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
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


# Pydantic Models (for API serialization and MongoDB)
class ObjectIdStr(str):
    """String form of MongoDB ObjectId for transport."""
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        return handler.generate_schema(str)


# Shared components
class TenantScoped(BaseModel):
    orgId: ObjectIdStr = Field(description="Tenant/org scope")
    userId: Optional[ObjectIdStr] = Field(None, description="Actor within tenant")


class AuditMeta(BaseModel):
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = None
    deletedAt: Optional[datetime] = None


# Users and auth
class UserSchema(BaseModel):
    userId: ObjectIdStr
    orgId: ObjectIdStr
    email: EmailStr
    role: str = Field(pattern="^(admin|analyst|reader)$")
    mfaEnabled: bool = False
    preferences: Dict[str, Any] = {}


class AuditEvent(BaseModel):
    eventId: ObjectIdStr
    orgId: ObjectIdStr
    actorUserId: ObjectIdStr
    action: str
    targetType: str
    targetId: ObjectIdStr
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}


# Trading journal
class Instrument(BaseModel):
    underlying: str
    optionType: str = Field(pattern="^(CALL|PUT)$")
    strike: float
    expiry: date


class TradeSchema(BaseModel):
    tenant: TenantScoped
    audit: AuditMeta
    tradeId: ObjectIdStr
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
    regimeTagIds: List[str] = []
    journalEntryIds: List[ObjectIdStr] = []
    screenshotIds: List[ObjectIdStr] = []
    realizedPnL: Optional[float] = None
    unrealizedPnL: Optional[float] = None


class ChecklistItem(BaseModel):
    label: str
    checked: bool = False


class JournalEntry(BaseModel):
    tenant: TenantScoped
    audit: AuditMeta

    entryId: ObjectIdStr
    tradeId: Optional[ObjectIdStr] = None
    setup: Optional[str] = None
    thesis: Optional[str] = None
    riskPlan: Optional[str] = None
    emotions: Optional[str] = None
    checklistItems: List[ChecklistItem] = []
    tags: List[str] = []
    screenshotIds: List[ObjectIdStr] = []


class NotebookNote(BaseModel):
    tenant: TenantScoped
    audit: AuditMeta

    noteId: ObjectIdStr
    title: str
    markdown: str
    backlinks: Dict[str, List[ObjectIdStr]] = Field(default_factory=dict)
    version: int = 1


# Market factors and analytics
class MarketFactorValues(BaseModel):
    VIX: Optional[float] = None
    breadth: Optional[float] = None
    trend: Optional[float] = None
    volRegime: Optional[str] = None
    liquidityProxy: Optional[float] = None


class MarketFactor(BaseModel):
    tenant: TenantScoped
    audit: AuditMeta

    factorId: ObjectIdStr
    date: date
    values: MarketFactorValues
    notes: Optional[str] = None
    tags: List[str] = []


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
    tenant: TenantScoped
    audit: AuditMeta

    snapshotId: ObjectIdStr
    granularity: str = Field(pattern="^(daily|weekly|monthly)$")
    periodStart: date
    periodEnd: date
    metrics: AnalyticsMetrics
    cohorts: CohortView


class Attachment(BaseModel):
    tenant: TenantScoped
    audit: AuditMeta

    fileId: ObjectIdStr
    type: str = Field(pattern="^(screenshot|csv)$")
    url: str
    checksum: str
    tradeId: Optional[ObjectIdStr] = None
    journalEntryId: Optional[ObjectIdStr] = None


# Time tracking and habits
class BreakBlock(BaseModel):
    start: datetime
    end: datetime
    type: str = Field(pattern="^(break|lunch)$")


class RuleCheck(BaseModel):
    label: str
    checked: bool


class Session(BaseModel):
    tenant: TenantScoped
    audit: AuditMeta

    sessionId: ObjectIdStr
    type: str = Field(pattern="^(trading|research|review)$")
    clockIn: datetime
    clockOut: Optional[datetime] = None
    breaks: List[BreakBlock] = []
    lunch: Optional[BreakBlock] = None
    notes: Optional[str] = None
    ruleChecklist: List[RuleCheck] = []
    tags: List[str] = []
    adherenceScore: Optional[float] = None


class BehaviorEvent(BaseModel):
    tenant: TenantScoped
    audit: AuditMeta

    eventId: ObjectIdStr
    timestamp: datetime
    type: str = Field(pattern="^(emotion|rule_violation|adherence)$")
    details: Dict[str, Any] = {}
    tradeId: Optional[ObjectIdStr] = None
    sessionId: Optional[ObjectIdStr] = None


class ImportJob(BaseModel):
    tenant: TenantScoped
    audit: AuditMeta

    jobId: ObjectIdStr
    source: str
    mappingTemplateId: Optional[str] = None
    status: str = Field(pattern="^(PENDING|RUNNING|COMPLETED|FAILED)$")
    stats: Dict[str, int] = {}
    errors: List[Dict[str, Any]] = []

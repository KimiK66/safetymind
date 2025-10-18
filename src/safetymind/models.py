from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any

from pydantic import BaseModel, Field, validator
from sqlmodel import SQLModel, Field as ORMField, JSON, Relationship


class EventType(str, Enum):
    NearMiss = "NearMiss"
    Incident = "Incident"
    Accident = "Accident"


class Consequence(str, Enum):
    Injury = "Injury"
    Environmental = "Environmental"
    AssetDamage = "AssetDamage"
    ProcessSafety = "ProcessSafety"
    Security = "Security"
    Other = "Other"


class Severity(str, Enum):
    Insignificant = "Insignificant"
    Minor = "Minor"
    Moderate = "Moderate"
    Major = "Major"
    Catastrophic = "Catastrophic"


class ReportStatus(str, Enum):
    Draft = "Draft"
    Submitted = "Submitted"
    UnderReview = "UnderReview"
    Closed = "Closed"


class ReportBase(SQLModel):
    title: str = ORMField(index=True)
    description: str
    event_type: EventType = ORMField(index=True)
    consequence: Optional[Consequence] = ORMField(default=None, index=True)
    severity: Optional[Severity] = ORMField(default=None, index=True)
    location: Optional[str] = ORMField(default=None, index=True)
    activity: Optional[str] = ORMField(default=None, index=True)
    status: ReportStatus = ORMField(default=ReportStatus.Submitted, index=True)
    occurred_at: datetime = ORMField(default_factory=datetime.utcnow, index=True)
    reported_by: Optional[str] = None
    
    # Enhanced incident fields
    witnesses: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    equipment_involved: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    weather_conditions: Optional[str] = ORMField(default=None, index=True)
    time_of_day: Optional[str] = ORMField(default=None, index=True)
    injury_details: Optional[Dict[str, Any]] = ORMField(default=None, sa_type=JSON)
    environmental_impact: Optional[Dict[str, Any]] = ORMField(default=None, sa_type=JSON)
    cost_estimate: Optional[float] = ORMField(default=None, index=True)
    images: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    # video_url removed for performance optimization
    voice_recording_url: Optional[str] = ORMField(default=None, index=True)
    similar_incidents: Optional[List[int]] = ORMField(default=None, sa_type=JSON)
    mem0_context: Optional[Dict[str, Any]] = ORMField(default=None, sa_type=JSON)
    
    # AI Analysis fields
    ai_analysis: Optional[Dict[str, object]] = ORMField(default=None, sa_type=JSON)
    immediate_causes: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    underlying_causes: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    risk_level: Optional[str] = ORMField(default=None, index=True)
    extra: Optional[Dict[str, str]] = ORMField(default=None, sa_type=JSON)


class Report(ReportBase, table=True):
    id: Optional[int] = ORMField(default=None, primary_key=True)


class ReportCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Report title")
    description: str = Field(..., min_length=10, max_length=5000, description="Detailed description of the incident")
    event_type: EventType
    consequence: Optional[Consequence] = None
    severity: Optional[Severity] = None
    location: Optional[str] = Field(None, max_length=100, description="Location where incident occurred")
    activity: Optional[str] = Field(None, max_length=100, description="Activity being performed")
    status: Optional[ReportStatus] = ReportStatus.Submitted
    occurred_at: Optional[datetime] = None
    reported_by: Optional[str] = Field(None, max_length=100, description="Name of person reporting")
    # AI Analysis fields (optional for creation)
    ai_analysis: Optional[Dict[str, object]] = Field(default=None, description="AI analysis results")
    immediate_causes: Optional[List[str]] = Field(default=None, description="Immediate causes identified by AI")
    underlying_causes: Optional[List[str]] = Field(default=None, description="Underlying causes identified by AI")
    risk_level: Optional[str] = Field(default=None, description="Risk level assessment")
    extra: Optional[Dict[str, str]] = Field(default=None, description="Additional custom fields")
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        if len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        return v.strip()
    
    @validator('occurred_at', pre=True)
    def validate_occurred_at(cls, v):
        if v is None:
            return datetime.utcnow()
        return v


class ReportRead(BaseModel):
    id: int
    title: str
    description: str
    event_type: EventType
    consequence: Optional[Consequence]
    severity: Optional[Severity]
    location: Optional[str]
    activity: Optional[str]
    status: ReportStatus
    occurred_at: datetime
    reported_by: Optional[str]
    # AI Analysis fields
    ai_analysis: Optional[Dict[str, object]]
    immediate_causes: Optional[List[str]]
    underlying_causes: Optional[List[str]]
    risk_level: Optional[str]
    extra: Optional[Dict[str, str]]

    class Config:
        from_attributes = True


class ReportSearchFilters(BaseModel):
    q: Optional[str] = Field(default=None, description="Keyword search across title/description")
    event_type: Optional[EventType] = None
    consequence: Optional[Consequence] = None
    severity: Optional[Severity] = None
    risk_level: Optional[str] = None
    status: Optional[ReportStatus] = None
    location: Optional[str] = None
    activity: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    limit: int = 50
    offset: int = 0


class AnalyticsSummary(BaseModel):
    total_reports: int
    by_event_type: Dict[str, int]
    by_consequence: Dict[str, int]
    by_severity: Dict[str, int]
    severity_index: float


class BenchmarkResult(BaseModel):
    metric: str
    unit: str
    organization_value: float
    benchmark_value: float
    delta: float
    interpretation: str


# New Models for Enhanced SafetyMind

class UserProfile(SQLModel, table=True):
    id: Optional[int] = ORMField(default=None, primary_key=True)
    user_id: str = ORMField(index=True, unique=True)
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    common_locations: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    typical_activities: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    reporting_preferences: Optional[Dict[str, Any]] = ORMField(default=None, sa_type=JSON)
    voice_settings: Optional[Dict[str, Any]] = ORMField(default=None, sa_type=JSON)
    created_at: datetime = ORMField(default_factory=datetime.utcnow)
    updated_at: datetime = ORMField(default_factory=datetime.utcnow)


class SafetyProtocol(SQLModel, table=True):
    id: Optional[int] = ORMField(default=None, primary_key=True)
    name: str = ORMField(index=True)
    category: str = ORMField(index=True)
    description: str
    requirements: Optional[Dict[str, Any]] = ORMField(default=None, sa_type=JSON)
    applicable_event_types: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    applicable_locations: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    applicable_activities: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    severity_threshold: Optional[str] = None
    compliance_checklist: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    created_by: Optional[str] = None
    created_at: datetime = ORMField(default_factory=datetime.utcnow)
    updated_at: datetime = ORMField(default_factory=datetime.utcnow)


class IncidentPattern(SQLModel, table=True):
    id: Optional[int] = ORMField(default=None, primary_key=True)
    pattern_name: str = ORMField(index=True)
    pattern_type: str = ORMField(index=True)  # recurring, seasonal, equipment, location
    description: str
    frequency: int = ORMField(default=0)
    severity_trend: Optional[str] = None
    common_causes: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    common_locations: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    common_activities: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    prevention_measures: Optional[List[str]] = ORMField(default=None, sa_type=JSON)
    related_incidents: Optional[List[int]] = ORMField(default=None, sa_type=JSON)
    confidence_score: float = ORMField(default=0.0)
    last_occurrence: Optional[datetime] = None
    created_at: datetime = ORMField(default_factory=datetime.utcnow)
    updated_at: datetime = ORMField(default_factory=datetime.utcnow)


class VoiceInput(BaseModel):
    audio_data: bytes
    transcript: Optional[str] = None
    confidence: Optional[float] = None
    language: Optional[str] = "en"
    duration: Optional[float] = None


class VoiceResponse(BaseModel):
    text: str
    audio_url: Optional[str] = None
    duration: Optional[float] = None


# Video generation models removed for performance optimization


class MemoryContext(BaseModel):
    user_id: str
    context_type: str  # user_preference, incident_pattern, safety_protocol
    data: Dict[str, Any]
    relevance_score: float
    last_accessed: datetime


class GroqAnalysisResult(BaseModel):
    enhanced_analysis: Dict[str, Any]
    industry_benchmarks: Dict[str, Any]
    similar_incidents_web: List[Dict[str, Any]]
    best_practices: List[str]
    recommendations: List[str]
    confidence_scores: Dict[str, float]

import os
from contextlib import contextmanager
from typing import Iterable, List, Optional

from sqlmodel import SQLModel, Session, create_engine, select

from .models import Report, ReportCreate, ReportSearchFilters
from .config import DATABASE_URL

# Create database engine
def get_engine():
    database_url = DATABASE_URL
    
    if database_url.startswith("postgresql"):
        # Supabase PostgreSQL
        engine = create_engine(database_url, echo=False)
    else:
        # Local SQLite
        engine = create_engine(database_url, echo=False)
    
    return engine

_engine = get_engine()


def init_db() -> None:
    SQLModel.metadata.create_all(_engine)


@contextmanager
def session_scope() -> Iterable[Session]:
    session = Session(_engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_report(payload: ReportCreate) -> Report:
    with session_scope() as session:
        report = Report(**payload.model_dump())
        session.add(report)
        session.flush()
        session.refresh(report)
        # Create a new Report object with the data to avoid session issues
        return Report(
            id=report.id,
            title=report.title,
            description=report.description,
            event_type=report.event_type,
            consequence=report.consequence,
            severity=report.severity,
            location=report.location,
            activity=report.activity,
            status=report.status,
            occurred_at=report.occurred_at,
            reported_by=report.reported_by,
            ai_analysis=report.ai_analysis,
            immediate_causes=report.immediate_causes,
            underlying_causes=report.underlying_causes,
            risk_level=report.risk_level,
            extra=report.extra
        )


def get_report(report_id: int) -> Optional[Report]:
    with session_scope() as session:
        report = session.get(Report, report_id)
        if not report:
            return None
        # Create a new Report object to avoid session issues
        return Report(
            id=report.id,
            title=report.title,
            description=report.description,
            event_type=report.event_type,
            consequence=report.consequence,
            severity=report.severity,
            location=report.location,
            activity=report.activity,
            status=report.status,
            occurred_at=report.occurred_at,
            reported_by=report.reported_by,
            ai_analysis=report.ai_analysis,
            immediate_causes=report.immediate_causes,
            underlying_causes=report.underlying_causes,
            risk_level=report.risk_level,
            extra=report.extra
        )


def search_reports(filters: ReportSearchFilters) -> List[Report]:
    with session_scope() as session:
        query = select(Report)
        if filters.q:
            like = f"%{filters.q}%"
            query = query.where((Report.title.like(like)) | (Report.description.like(like)))
        if filters.event_type:
            query = query.where(Report.event_type == filters.event_type)
        if filters.consequence:
            query = query.where(Report.consequence == filters.consequence)
        if filters.severity:
            query = query.where(Report.severity == filters.severity)
        if filters.risk_level:
            query = query.where(Report.risk_level == filters.risk_level)
        if filters.status:
            query = query.where(Report.status == filters.status)
        if filters.location:
            query = query.where(Report.location == filters.location)
        if filters.activity:
            query = query.where(Report.activity == filters.activity)
        if filters.start:
            query = query.where(Report.occurred_at >= filters.start)
        if filters.end:
            query = query.where(Report.occurred_at <= filters.end)
        query = query.offset(filters.offset).limit(filters.limit)
        reports = list(session.exec(query).all())
        # Create new Report objects to avoid session issues
        return [
            Report(
                id=r.id,
                title=r.title,
                description=r.description,
                event_type=r.event_type,
                consequence=r.consequence,
                severity=r.severity,
                location=r.location,
                activity=r.activity,
                status=r.status,
                occurred_at=r.occurred_at,
                reported_by=r.reported_by,
                ai_analysis=r.ai_analysis,
                immediate_causes=r.immediate_causes,
                underlying_causes=r.underlying_causes,
                risk_level=r.risk_level,
                extra=r.extra
            ) for r in reports
        ]



def update_report_status(report_id: int, new_status: str) -> bool:
    from .models import ReportStatus
    with session_scope() as session:
        report = session.get(Report, report_id)
        if not report:
            return False
        # cast string to enum if needed
        try:
            if not isinstance(new_status, ReportStatus):
                new_status = ReportStatus(new_status)  # type: ignore
        except Exception:
            return False
        report.status = new_status  # type: ignore
        session.add(report)
        return True


def add_capa_note(report_id: int, note: str, author: str) -> bool:
    with session_scope() as session:
        report = session.get(Report, report_id)
        if not report:
            return False
        extra = report.extra or {}
        prev = extra.get('capa', '') or ''
        line = f"[{author}] {note}"
        extra['capa'] = (prev + "\n" + line).strip() if prev else line
        report.extra = extra
        session.add(report)
        return True


def update_report_ai_analysis(
    report_id: int, 
    immediate_causes: list, 
    underlying_causes: list, 
    ai_analysis: dict, 
    risk_level: str
) -> bool:
    """Update a report with improved AI analysis."""
    with session_scope() as session:
        report = session.get(Report, report_id)
        if not report:
            return False
        
        # Update AI analysis fields
        report.immediate_causes = immediate_causes
        report.underlying_causes = underlying_causes
        report.ai_analysis = ai_analysis
        report.risk_level = risk_level
        
        session.add(report)
        return True

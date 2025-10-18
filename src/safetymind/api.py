import os
import csv
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Query, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import (
    ReportCreate,
    ReportRead,
    ReportSearchFilters,
    AnalyticsSummary,
    VoiceInput,
    VoiceResponse,
    MemoryContext,
    GroqAnalysisResult,
)
from .storage import init_db, create_report, search_reports, get_report
from .ai import analyze_report
from .benchmark import load_oil_gas_benchmark, compute_org_metrics, compare_to_benchmark
from .voice import initialize_elevenlabs, transcribe_audio, parse_voice_input, generate_voice_response
from .memory import initialize_mem0, store_user_preference, get_user_context, get_similar_incidents
from .groq_analysis import initialize_groq, analyze_with_groq
# Video generation removed for performance optimization
from .config import (
    BENCHMARK_PATH, WEB_DIR, USERS, API_TITLE, API_DESCRIPTION, API_VERSION,
    CORS_ORIGINS, CORS_CREDENTIALS, CORS_METHODS, CORS_HEADERS,
    EXPORT_MAX_RECORDS, EXPORT_REDACT_PII_DEFAULT, ELEVENLABS_API_KEY, GROQ_API_KEY, MEM0_API_KEY
)

# Basic Auth (demo only)
basic_security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(basic_security)):
    import secrets
    user = USERS.get(credentials.username)
    if not user or not secrets.compare_digest(user["password"], credentials.password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"username": credentials.username, "role": user["role"]}


def require_role(role: str):
    def _dep(user = Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _dep


class StatusUpdate(BaseModel):
    new_status: str


class CapaNote(BaseModel):
    note: str


def create_app() -> FastAPI:
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_CREDENTIALS,
        allow_methods=CORS_METHODS,
        allow_headers=CORS_HEADERS,
    )

    # Mount static files
    if WEB_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    # Serve the main web interface
    @app.get("/")
    async def read_root():
        index_file = WEB_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "SafetyMind API is running. Visit /docs for API documentation."}

    @app.get("/health")
    def api_health():
        """Health check endpoint for production monitoring."""
        try:
            # Basic health checks
            from .storage import init_db
            init_db()  # This will create tables if they don't exist
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "database": "connected",
                "services": {
                    "elevenlabs": "configured" if ELEVENLABS_API_KEY else "not_configured",
                    "groq": "configured" if GROQ_API_KEY else "not_configured",
                    "mem0": "configured" if MEM0_API_KEY else "not_configured"
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    # Initialize database
    init_db()

    @app.post("/reports", response_model=ReportRead)
    def api_create_report(payload: ReportCreate, user=Depends(get_current_user)):
        try:
            # Run comprehensive AI analysis
            ai = analyze_report(payload)
            
            # Fill optional fields if missing
            if payload.consequence is None and ai.get("consequence"):
                payload.consequence = ai["consequence"]  # type: ignore
            if payload.severity is None and ai.get("severity_band"):
                payload.severity = ai["severity_band"]  # type: ignore
            
            # Store AI analysis results
            payload.ai_analysis = ai
            payload.immediate_causes = ai.get("immediate_causes", [])
            payload.underlying_causes = ai.get("underlying_causes", [])
            payload.risk_level = ai.get("risk_level")
            
            report = create_report(payload)
            return ReportRead.model_validate(report)
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")

    @app.get("/reports", response_model=List[ReportRead])
    def api_search_reports(
        q: Optional[str] = None,
        event_type: Optional[str] = None,
        consequence: Optional[str] = None,
        severity: Optional[str] = None,
        risk_level: Optional[str] = None,
        status: Optional[str] = None,
        location: Optional[str] = None,
        activity: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ):
        filters = ReportSearchFilters(
            q=q,
            event_type=event_type,
            consequence=consequence,
            severity=severity,
            risk_level=risk_level,
            status=status,
            location=location,
            activity=activity,
            start=start,
            end=end,
            limit=limit,
            offset=offset,
        )
        reports = search_reports(filters)
        return [ReportRead.model_validate(r) for r in reports]

    @app.get("/reports/{report_id}", response_model=ReportRead)
    def api_get_report(report_id: int):
        report = get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return ReportRead.model_validate(report)

    @app.get("/export")
    def api_export(format: str = Query("csv", pattern="^(csv|json)$"), redact_pii: bool = EXPORT_REDACT_PII_DEFAULT):
        filters = ReportSearchFilters(limit=EXPORT_MAX_RECORDS)
        reports = search_reports(filters)
        rows = []
        for r in reports:
            item = ReportRead.model_validate(r).model_dump()
            if redact_pii and item.get("reported_by"):
                item["reported_by"] = "REDACTED"
            rows.append(item)
        if format == "json":
            return rows
        # CSV export
        if not rows:
            return ""
        fieldnames = list(rows[0].keys())
        from io import StringIO

        buf = StringIO()
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue()

    @app.get("/analytics/summary", response_model=AnalyticsSummary)
    def api_summary():
        filters = ReportSearchFilters(limit=EXPORT_MAX_RECORDS)
        reports = search_reports(filters)
        total = len(reports)
        by_event = {}
        by_cons = {}
        by_sev = {}
        weights = {"Insignificant": 1, "Minor": 2, "Moderate": 3, "Major": 4, "Catastrophic": 5}
        weight_sum = 0
        for r in reports:
            # Use enum values instead of string representation
            event_type = r.event_type.value if hasattr(r.event_type, 'value') else str(r.event_type)
            by_event[event_type] = by_event.get(event_type, 0) + 1
            
            if r.consequence:
                consequence = r.consequence.value if hasattr(r.consequence, 'value') else str(r.consequence)
                by_cons[consequence] = by_cons.get(consequence, 0) + 1
            
            if r.severity:
                severity = r.severity.value if hasattr(r.severity, 'value') else str(r.severity)
                by_sev[severity] = by_sev.get(severity, 0) + 1
                weight_sum += weights.get(severity, 0)
        
        severity_index = (weight_sum / total) if total else 0.0
        return AnalyticsSummary(
            total_reports=total,
            by_event_type=by_event,
            by_consequence=by_cons,
            by_severity=by_sev,
            severity_index=severity_index,
        )

    @app.get("/analytics/benchmark")
    def api_benchmark():
        import pandas as pd

        # Organization metrics from current DB (approximation)
        filters = ReportSearchFilters(limit=EXPORT_MAX_RECORDS)
        reports = search_reports(filters)
        
        # Create a small DataFrame for metrics derivation
        data = {
            "hours_worked": [200000],
            "near_miss": [sum(1 for r in reports if r.event_type.value == "NearMiss")],
            "recordable_incident": [sum(1 for r in reports if r.event_type.value in ("Incident", "Accident"))],
            "severe": [sum(1 for r in reports if r.severity and r.severity.value in ("Major", "Catastrophic"))],
            "total_events": [len(reports)],
        }
        org_df = pd.DataFrame(data)
        org_metrics = compute_org_metrics(org_df)

        # Benchmark from CSV
        if not os.path.exists(BENCHMARK_PATH):
            return {"error": f"Benchmark not found at {BENCHMARK_PATH}"}
        ref_df = load_oil_gas_benchmark(BENCHMARK_PATH)
        ref_metrics = compute_org_metrics(ref_df)
        return compare_to_benchmark(org_metrics, ref_metrics)


    @app.post("/reports/{report_id}/status")
    def api_update_status(report_id: int, body: StatusUpdate, user=Depends(require_role("reviewer"))):
        from .storage import update_report_status
        ok = update_report_status(report_id, body.new_status)
        if not ok:
            raise HTTPException(status_code=400, detail="Invalid report or status")
        return {"ok": True, "report_id": report_id, "status": body.new_status}

    @app.post("/reports/{report_id}/capa")
    def api_add_capa(report_id: int, body: CapaNote, user=Depends(require_role("reviewer"))):
        from .storage import add_capa_note
        ok = add_capa_note(report_id, body.note, user.get("username", "reviewer"))
        if not ok:
            raise HTTPException(status_code=400, detail="Invalid report")
        return {"ok": True}

    # Voice Input Endpoints
    @app.post("/reports/voice", response_model=VoiceResponse)
    def api_process_voice_input(audio_file: UploadFile = File(...), user=Depends(get_current_user)):
        """Process voice input and extract structured data."""
        try:
            # Read audio file content
            audio_content = audio_file.file.read()
            
            # Transcribe audio
            transcript = transcribe_audio(audio_content)
            if not transcript:
                raise HTTPException(status_code=400, detail="Failed to transcribe audio")
            
            # Parse voice input to extract fields
            parsed_fields = parse_voice_input(transcript)
            
            return VoiceResponse(
                transcript=transcript,
                parsed_fields=parsed_fields,
                confidence=parsed_fields.get("confidence", 0.0)
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

    @app.post("/reports/voice/field")
    def api_process_field_voice(
        audio_file: UploadFile = File(...), 
        field: str = Form(...), 
        user=Depends(get_current_user)
    ):
        """Process voice input for a specific field."""
        try:
            # Read audio file content
            audio_content = audio_file.file.read()
            
            transcript = transcribe_audio(audio_content)
            if not transcript:
                raise HTTPException(status_code=400, detail="Failed to transcribe audio")
            
            # Simple field-specific parsing
            parsed_fields = parse_voice_input(transcript)
            field_value = parsed_fields.get(field, transcript)
            
            return {"field": field, "value": field_value, "transcript": transcript}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Field voice processing failed: {str(e)}")

    @app.post("/reports/voice/parse")
    def api_parse_voice_transcript(
        request: dict,
        user=Depends(get_current_user)
    ):
        """Parse voice transcript and extract structured data."""
        try:
            transcript = request.get("transcript", "")
            if not transcript:
                raise HTTPException(status_code=400, detail="No transcript provided")
            
            # Parse voice input to extract fields
            parsed_fields = parse_voice_input(transcript)
            
            return {
                "transcript": transcript,
                "parsed_fields": parsed_fields,
                "success": True
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Voice parsing failed: {str(e)}")

    # Video generation endpoints removed for performance optimization
    # Memory Endpoints
    @app.get("/memory/similar/{report_id}")
    def api_get_similar_incidents(report_id: int, user=Depends(get_current_user)):
        """Get similar incidents from memory."""
        try:
            report = get_report(report_id)
            if not report:
                raise HTTPException(status_code=404, detail="Report not found")
            
            similar_incidents = get_similar_incidents(report)
            return {
                "report_id": report_id,
                "similar_incidents": similar_incidents,
                "count": len(similar_incidents)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get similar incidents: {str(e)}")

    @app.get("/memory/patterns")
    def api_get_incident_patterns(user=Depends(get_current_user)):
        """Get learned incident patterns."""
        try:
            # This would typically query the IncidentPattern table
            # For now, return mock data
            patterns = [
                {
                    "pattern_name": "Equipment Failure Pattern",
                    "pattern_type": "equipment",
                    "frequency": 5,
                    "common_causes": ["Corrosion", "Wear", "Improper maintenance"],
                    "prevention_measures": ["Regular inspection", "Preventive maintenance"]
                }
            ]
            return {"patterns": patterns, "count": len(patterns)}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get patterns: {str(e)}")

    @app.get("/memory/protocols")
    def api_get_safety_protocols(user=Depends(get_current_user)):
        """Get organization safety protocols."""
        try:
            # This would typically query the SafetyProtocol table
            # For now, return mock data
            protocols = [
                {
                    "name": "Gas Leak Response Protocol",
                    "category": "Emergency Response",
                    "description": "Standard procedures for gas leak incidents",
                    "requirements": ["Immediate evacuation", "Emergency shutdown", "Notify authorities"]
                }
            ]
            return {"protocols": protocols, "count": len(protocols)}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get protocols: {str(e)}")

    @app.post("/memory/protocol")
    def api_add_safety_protocol(protocol_data: dict, user=Depends(require_role("reviewer"))):
        """Add a new safety protocol."""
        try:
            # This would typically save to the SafetyProtocol table
            # For now, return success
            return {"ok": True, "protocol_id": "new_protocol_001"}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add protocol: {str(e)}")

    # Groq Analysis Endpoints
    @app.get("/groq/recommendations/{report_id}")
    def api_get_groq_recommendations(report_id: int, user=Depends(get_current_user)):
        """Get Groq-enhanced recommendations for a report."""
        try:
            report = get_report(report_id)
            if not report:
                raise HTTPException(status_code=404, detail="Report not found")
            
            # Convert report to dict for Groq analysis
            report_data = {
                "title": report.title,
                "description": report.description,
                "event_type": report.event_type.value if report.event_type else None,
                "location": report.location,
                "activity": report.activity,
                "consequence": report.consequence.value if report.consequence else None,
                "severity": report.severity.value if report.severity else None
            }
            
            groq_analysis = analyze_with_groq(report_data)
            return groq_analysis
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Groq analysis failed: {str(e)}")

    @app.get("/groq/industry-data")
    def api_get_industry_data(user=Depends(get_current_user)):
        """Get real-time industry benchmark data."""
        try:
            # This would typically fetch real-time data from industry sources
            # For now, return mock data
            industry_data = {
                "oil_gas_benchmark": {
                    "near_miss_rate": 2.5,
                    "incident_rate": 0.8,
                    "severe_share": 0.15
                },
                "last_updated": "2024-01-15T10:30:00Z",
                "source": "IOGP Safety Performance Indicators"
            }
            return industry_data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get industry data: {str(e)}")

    # User Profile Endpoints
    @app.get("/user/profile")
    def api_get_user_profile(user=Depends(get_current_user)):
        """Get user profile and preferences."""
        try:
            user_context = get_user_context(user["username"])
            return {
                "user_id": user["username"],
                "role": user["role"],
                "preferences": user_context or {},
                "common_locations": ["Platform A", "Compression Station B"],
                "typical_activities": ["maintenance", "inspection", "repair"]
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")

    @app.post("/user/preferences")
    def api_update_user_preferences(preferences: dict, user=Depends(get_current_user)):
        """Update user preferences."""
        try:
            stored = store_user_preference(user["username"], preferences)
            return {"ok": stored, "user_id": user["username"]}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

    return app

"""
SafetyMind Background Tasks Module
Handles asynchronous processing for resource-intensive operations.
"""

import asyncio
import threading
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import json

from .models import Report, VideoGenerationResult
from .voice import transcribe_audio, parse_voice_input
from .memory import store_incident_pattern, update_memory_from_incident
from .video_generation import generate_incident_video
from .groq_analysis import analyze_with_groq


class TaskStatus:
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackgroundTask:
    """Represents a background task."""
    
    def __init__(self, task_id: str, task_type: str, payload: Dict[str, Any]):
        self.task_id = task_id
        self.task_type = task_type
        self.payload = payload
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.result = None
        self.error = None
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.thread = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class TaskManager:
    """Manages background tasks."""
    
    def __init__(self):
        self.tasks: Dict[str, BackgroundTask] = {}
        self.task_counter = 0
        self.max_concurrent_tasks = 3
        self.running_tasks = 0
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        self.task_counter += 1
        return f"task_{self.task_counter}_{int(time.time())}"
    
    def create_task(self, task_type: str, payload: Dict[str, Any]) -> str:
        """Create a new background task."""
        task_id = self._generate_task_id()
        task = BackgroundTask(task_id, task_type, payload)
        self.tasks[task_id] = task
        
        # Start task if we have capacity
        if self.running_tasks < self.max_concurrent_tasks:
            self._start_task(task)
        
        return task_id
    
    def _start_task(self, task: BackgroundTask):
        """Start a task in a separate thread."""
        if task.status != TaskStatus.PENDING:
            return
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        self.running_tasks += 1
        
        # Create thread based on task type
        if task.task_type == "voice_processing":
            task.thread = threading.Thread(target=self._process_voice_task, args=(task,))
        elif task.task_type == "video_generation":
            task.thread = threading.Thread(target=self._process_video_task, args=(task,))
        elif task.task_type == "memory_update":
            task.thread = threading.Thread(target=self._process_memory_task, args=(task,))
        elif task.task_type == "groq_analysis":
            task.thread = threading.Thread(target=self._process_groq_task, args=(task,))
        else:
            task.status = TaskStatus.FAILED
            task.error = f"Unknown task type: {task.task_type}"
            self.running_tasks -= 1
            return
        
        task.thread.start()
    
    def _process_voice_task(self, task: BackgroundTask):
        """Process voice input task."""
        try:
            task.progress = 10
            
            # Extract audio data
            audio_data = task.payload.get("audio_data")
            if not audio_data:
                raise ValueError("No audio data provided")
            
            task.progress = 30
            
            # Transcribe audio
            transcript = transcribe_audio(audio_data)
            if not transcript:
                raise ValueError("Failed to transcribe audio")
            
            task.progress = 60
            
            # Parse voice input
            parsed_fields = parse_voice_input(transcript)
            
            task.progress = 90
            
            # Store result
            task.result = {
                "transcript": transcript,
                "parsed_fields": parsed_fields,
                "confidence": parsed_fields.get("confidence", 0.0)
            }
            
            task.progress = 100
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
        
        finally:
            task.completed_at = datetime.utcnow()
            self.running_tasks -= 1
            self._check_pending_tasks()
    
    def _process_video_task(self, task: BackgroundTask):
        """Process video generation task."""
        try:
            task.progress = 5
            
            # Extract report data
            report_data = task.payload.get("report_data")
            if not report_data:
                raise ValueError("No report data provided")
            
            # Create Report object
            from .models import EventType, Consequence, Severity
            report = Report(
                id=report_data.get("id", 0),
                title=report_data.get("title", ""),
                description=report_data.get("description", ""),
                event_type=EventType(report_data.get("event_type", "Incident")),
                location=report_data.get("location"),
                activity=report_data.get("activity"),
                weather_conditions=report_data.get("weather_conditions"),
                time_of_day=report_data.get("time_of_day"),
                equipment_involved=report_data.get("equipment_involved", []),
                consequence=Consequence(report_data.get("consequence")) if report_data.get("consequence") else None,
                severity=Severity(report_data.get("severity")) if report_data.get("severity") else None,
                created_at=datetime.utcnow()
            )
            
            task.progress = 15
            
            # Generate video
            video_result = generate_incident_video(report)
            
            task.progress = 95
            
            # Store result
            task.result = {
                "video_result": video_result.to_dict() if hasattr(video_result, 'to_dict') else video_result,
                "report_id": report.id,
                "status": video_result.status if hasattr(video_result, 'status') else "completed"
            }
            
            task.progress = 100
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
        
        finally:
            task.completed_at = datetime.utcnow()
            self.running_tasks -= 1
            self._check_pending_tasks()
    
    def _process_memory_task(self, task: BackgroundTask):
        """Process memory update task."""
        try:
            task.progress = 10
            
            # Extract report data
            report_data = task.payload.get("report_data")
            if not report_data:
                raise ValueError("No report data provided")
            
            task.progress = 30
            
            # Update memory with incident data
            memory_result = update_memory_from_incident(report_data)
            
            task.progress = 70
            
            # Store incident pattern if applicable
            pattern_result = store_incident_pattern(report_data)
            
            task.progress = 90
            
            # Store result
            task.result = {
                "memory_updated": memory_result,
                "pattern_stored": pattern_result,
                "report_id": report_data.get("id")
            }
            
            task.progress = 100
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
        
        finally:
            task.completed_at = datetime.utcnow()
            self.running_tasks -= 1
            self._check_pending_tasks()
    
    def _process_groq_task(self, task: BackgroundTask):
        """Process Groq analysis task."""
        try:
            task.progress = 10
            
            # Extract report data
            report_data = task.payload.get("report_data")
            if not report_data:
                raise ValueError("No report data provided")
            
            task.progress = 30
            
            # Run Groq analysis
            groq_result = analyze_with_groq(report_data)
            
            task.progress = 90
            
            # Store result
            task.result = {
                "groq_analysis": groq_result,
                "report_id": report_data.get("id"),
                "analysis_type": "enhanced_recommendations"
            }
            
            task.progress = 100
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
        
        finally:
            task.completed_at = datetime.utcnow()
            self.running_tasks -= 1
            self._check_pending_tasks()
    
    def _check_pending_tasks(self):
        """Check for pending tasks to start."""
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING and self.running_tasks < self.max_concurrent_tasks:
                self._start_task(task)
                break
    
    def get_task(self, task_id: str) -> Optional[BackgroundTask]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status."""
        task = self.get_task(task_id)
        return task.to_dict() if task else None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            
            if task.status == TaskStatus.RUNNING:
                self.running_tasks -= 1
                self._check_pending_tasks()
            
            return True
        
        return False
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks."""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                task.completed_at and task.completed_at.timestamp() < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        return len(tasks_to_remove)


# Global task manager instance
task_manager = TaskManager()


# Convenience functions for creating tasks
def create_voice_processing_task(audio_data: bytes) -> str:
    """Create a voice processing task."""
    return task_manager.create_task("voice_processing", {"audio_data": audio_data})


def create_video_generation_task(report_data: Dict[str, Any]) -> str:
    """Create a video generation task."""
    return task_manager.create_task("video_generation", {"report_data": report_data})


def create_memory_update_task(report_data: Dict[str, Any]) -> str:
    """Create a memory update task."""
    return task_manager.create_task("memory_update", {"report_data": report_data})


def create_groq_analysis_task(report_data: Dict[str, Any]) -> str:
    """Create a Groq analysis task."""
    return task_manager.create_task("groq_analysis", {"report_data": report_data})


# Task status functions
def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get task status."""
    return task_manager.get_task_status(task_id)


def cancel_task(task_id: str) -> bool:
    """Cancel a task."""
    return task_manager.cancel_task(task_id)


def cleanup_old_tasks(max_age_hours: int = 24) -> int:
    """Clean up old tasks."""
    return task_manager.cleanup_old_tasks(max_age_hours)


# Background cleanup task
def start_cleanup_scheduler():
    """Start background cleanup scheduler."""
    def cleanup_worker():
        while True:
            try:
                cleanup_old_tasks()
                time.sleep(3600)  # Run every hour
            except Exception as e:
                print(f"Cleanup scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    return cleanup_thread


# Initialize cleanup scheduler
cleanup_thread = start_cleanup_scheduler()

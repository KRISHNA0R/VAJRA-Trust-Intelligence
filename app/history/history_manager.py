"""
Detection History Manager
Manages detection job history with user isolation
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class HistoryManager:
    """Manages detection history for users"""

    def __init__(self, data_dir: str = "data/jobs"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _load_metadata(self, job_id: str) -> Optional[Dict]:
        """Load job metadata"""
        job_dir = self.data_dir / job_id
        metadata_file = job_dir / "metadata.json"

        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _save_metadata(self, job_id: str, metadata: Dict):
        """Save job metadata"""
        job_dir = self.data_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        metadata_file = job_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def _load_timeline(self, job_id: str) -> Optional[Dict]:
        """Load timeline data for DeepfakeBench jobs"""
        job_dir = self.data_dir / job_id
        timeline_file = job_dir / "timeline.json"

        if not timeline_file.exists():
            return None

        try:
            with open(timeline_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def create_job_metadata(
        self,
        job_id: str,
        username: str,
        filename: str,
        detection_type: str,
        model: str = None
    ):
        """Create metadata for a new detection job"""
        metadata = {
            "job_id": job_id,
            "username": username,
            "filename": filename,
            "detection_type": detection_type,  # "trufor" or "deepfakebench"
            "model": model,  # For DeepfakeBench
            "created_at": datetime.now().isoformat(),
            "status": "processing",
            "completed_at": None,
            "result": None,
            "error": None
        }

        self._save_metadata(job_id, metadata)
        return metadata

    def update_job_status(self, job_id: str, status: str, result: Dict = None, error: str = None):
        """Update job status and result"""
        metadata = self._load_metadata(job_id)
        if not metadata:
            raise ValueError(f"Job {job_id} not found")

        metadata["status"] = status
        if status in ["completed", "failed"]:
            metadata["completed_at"] = datetime.now().isoformat()

        if result:
            metadata["result"] = result

        if error:
            metadata["error"] = error

        self._save_metadata(job_id, metadata)

    def get_job_details(self, job_id: str, username: str, role: str) -> Optional[Dict]:
        """
        Get detailed job information
        Users can only access their own jobs unless they're admin
        """
        metadata = self._load_metadata(job_id)
        if not metadata:
            return None

        # Check access permission
        if role != "admin" and metadata.get("username") != username:
            return None

        # Add timeline data if available
        timeline = self._load_timeline(job_id)
        if timeline:
            metadata["timeline"] = timeline

        # Check for generated reports
        job_dir = self.data_dir / job_id
        metadata["has_pdf"] = (job_dir / "report.pdf").exists()
        metadata["has_zip"] = (job_dir / "report.zip").exists()

        return metadata

    def get_user_history(
        self,
        username: str,
        role: str,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> Dict:
        """
        Get detection history for a user
        Admins can see all jobs, analysts only see their own
        """
        all_jobs = []

        # Scan all job directories
        for job_dir in self.data_dir.iterdir():
            if not job_dir.is_dir():
                continue

            metadata = self._load_metadata(job_dir.name)
            if not metadata:
                continue

            # Filter by user (unless admin)
            if role != "admin" and metadata.get("username") != username:
                continue

            # Filter by status if specified
            if status and metadata.get("status") != status:
                continue

            # Add lightweight summary (no full timeline)
            job_summary = {
                "job_id": metadata["job_id"],
                "filename": metadata["filename"],
                "detection_type": metadata["detection_type"],
                "model": metadata.get("model"),
                "created_at": metadata["created_at"],
                "completed_at": metadata.get("completed_at"),
                "status": metadata["status"],
                "verdict": metadata.get("result", {}).get("verdict") if metadata.get("result") else None,
                "score": metadata.get("result", {}).get("score") if metadata.get("result") else None
            }

            all_jobs.append(job_summary)

        # Sort by created_at timestamp (newest first)
        all_jobs.sort(key=lambda x: x["created_at"], reverse=True)

        # Apply pagination
        total = len(all_jobs)
        paginated_jobs = all_jobs[offset:offset + limit]

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "jobs": paginated_jobs
        }

    def get_statistics(self, username: str, role: str) -> Dict:
        """Get detection statistics for a user"""
        history = self.get_user_history(username, role, limit=10000)
        jobs = history["jobs"]

        total = len(jobs)
        completed = sum(1 for j in jobs if j["status"] == "completed")
        failed = sum(1 for j in jobs if j["status"] == "failed")
        processing = sum(1 for j in jobs if j["status"] == "processing")

        # Calculate verdicts
        real_count = sum(1 for j in jobs if j.get("verdict") == "real")
        fake_count = sum(1 for j in jobs if j.get("verdict") == "fake")

        # Calculate average score
        scores = [j["score"] for j in jobs if j.get("score") is not None]
        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "total_jobs": total,
            "completed": completed,
            "failed": failed,
            "processing": processing,
            "verdicts": {
                "real": real_count,
                "fake": fake_count
            },
            "average_score": round(avg_score, 2)
        }

    def delete_job(self, job_id: str, username: str, role: str) -> bool:
        """
        Delete a detection job
        Users can only delete their own jobs unless they're admin
        """
        metadata = self._load_metadata(job_id)
        if not metadata:
            return False

        # Check permission
        if role != "admin" and metadata.get("username") != username:
            raise PermissionError("You can only delete your own jobs")

        # Delete job directory
        job_dir = self.data_dir / job_id
        if job_dir.exists():
            shutil.rmtree(job_dir)
            return True

        return False

    def cleanup_old_jobs(self, days: int = 30) -> int:
        """
        Clean up jobs older than specified days
        Returns number of jobs deleted
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for job_dir in self.data_dir.iterdir():
            if not job_dir.is_dir():
                continue

            metadata = self._load_metadata(job_dir.name)
            if not metadata:
                continue

            try:
                created_at = datetime.fromisoformat(metadata["created_at"])
                if created_at < cutoff_date:
                    shutil.rmtree(job_dir)
                    deleted_count += 1
            except (ValueError, KeyError):
                continue

        return deleted_count


# Global instance
history_manager = HistoryManager()

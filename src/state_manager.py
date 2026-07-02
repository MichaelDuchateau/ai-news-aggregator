"""State management for tracking aggregator progress."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from src.models import WeeklyState, ProcessedURL, NewsItem


class StateManager:
    """Manages application state and processed URLs."""
    
    def __init__(self, state_dir: str = "state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.archive_dir = self.state_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)
        
        self.processed_urls_file = self.state_dir / "processed_urls.json"
        self.weekly_state_file = self.state_dir / "weekly_state.json"
        
        self.processed_urls = self._load_processed_urls()
        self.weekly_state = self._load_weekly_state()
    
    def _load_processed_urls(self) -> Dict[str, ProcessedURL]:
        """Load processed URLs from JSON."""
        if not self.processed_urls_file.exists():
            return {}
        
        with open(self.processed_urls_file, 'r') as f:
            data = json.load(f)
        
        # Guard against legacy format: {"processed_urls": [...], "last_updated": "..."}
        return {
            url: ProcessedURL(**info)
            for url, info in data.items()
            if isinstance(info, dict)
        }
    
    def _save_processed_urls(self):
        """Save processed URLs to JSON."""
        data = {
            url: item.model_dump(mode='json')
            for url, item in self.processed_urls.items()
        }
        
        with open(self.processed_urls_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_weekly_state(self) -> Optional[WeeklyState]:
        """Load current weekly state."""
        if not self.weekly_state_file.exists():
            return None
        
        with open(self.weekly_state_file, 'r') as f:
            data = json.load(f)
        
        return WeeklyState(**data)
    
    def _save_weekly_state(self):
        """Save current weekly state."""
        if self.weekly_state:
            with open(self.weekly_state_file, 'w') as f:
                json.dump(
                    self.weekly_state.model_dump(mode='json'), 
                    f, 
                    indent=2, 
                    default=str
                )
    
    def get_current_week(self, now: Optional[datetime] = None) -> str:
        """Get current ISO week string (e.g., '2025-W52')."""
        return (now or datetime.now()).strftime("%G-W%V")
    
    def init_new_week(self):
        """Initialize state for a new week."""
        current_week = self.get_current_week()
        
        # Archive old state if exists
        if self.weekly_state and self.weekly_state.week != current_week:
            self._archive_weekly_state()
        
        self.weekly_state = WeeklyState(
            week=current_week,
            stage="discovery",
            last_updated=datetime.now()
        )
        self._save_weekly_state()
    
    def _archive_weekly_state(self):
        """Move old weekly state to archive."""
        if not self.weekly_state:
            return
        
        archive_file = self.archive_dir / f"week_{self.weekly_state.week}.json"
        
        with open(archive_file, 'w') as f:
            json.dump(
                self.weekly_state.model_dump(mode='json'),
                f,
                indent=2,
                default=str
            )
    
    def is_url_processed(self, url: str) -> bool:
        """Check if URL has already been processed."""
        return url in self.processed_urls
    
    def mark_url_processed(self, url: str, status: str, week: str):
        """Mark a URL as processed."""
        self.processed_urls[url] = ProcessedURL(
            url=url,
            first_seen=datetime.now(),
            status=status,
            week=week
        )
        self._save_processed_urls()
    
    def update_stage(self, stage: str):
        """Update current processing stage."""
        if self.weekly_state:
            self.weekly_state.stage = stage
            self.weekly_state.last_updated = datetime.now()
            self._save_weekly_state()
    
    def add_discovered_url(self, url: str):
        """Add a discovered URL to this week's state."""
        if self.weekly_state and url not in self.weekly_state.discovered_urls:
            self.weekly_state.discovered_urls.append(url)
            self.weekly_state.items_discovered += 1
            self._save_weekly_state()
    
    def add_shortlisted_url(self, url: str):
        """Add a shortlisted URL."""
        if self.weekly_state and url not in self.weekly_state.shortlisted_urls:
            self.weekly_state.shortlisted_urls.append(url)
            self.weekly_state.items_shortlisted += 1
            self._save_weekly_state()
    
    def add_deep_dive_url(self, url: str):
        """Add a deep dive URL."""
        if self.weekly_state and url not in self.weekly_state.deep_dive_urls:
            self.weekly_state.deep_dive_urls.append(url)
            self.weekly_state.items_deep_dived += 1
            self._save_weekly_state()
    
    def get_status_summary(self) -> str:
        """Get a summary of current state."""
        if not self.weekly_state:
            return "No active weekly state"
        
        return f"""
Week: {self.weekly_state.week}
Stage: {self.weekly_state.stage}
Discovered: {self.weekly_state.items_discovered}
Shortlisted: {self.weekly_state.items_shortlisted}
Deep Dived: {self.weekly_state.items_deep_dived}
Last Updated: {self.weekly_state.last_updated}
"""

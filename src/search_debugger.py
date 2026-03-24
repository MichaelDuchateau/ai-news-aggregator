"""Search debugging and diagnostics module."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class SearchDebugger:
    """Logs and tracks search operations for debugging."""

    def __init__(self, log_dir: str = "state/search_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logs: List[Dict[str, Any]] = []

    def log_search(
        self,
        query: str,
        results_count: int,
        success: bool,
        error: str = None,
        raw_response: str = None,
        parsed_items: List[Dict] = None
    ):
        """Log a search operation."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results_count": results_count,
            "success": success,
            "error": error,
            "raw_response_preview": raw_response[:500] if raw_response else None,
            "parsed_items": parsed_items or []
        }

        self.logs.append(log_entry)

        # Save to file
        self._save_log()

        # Print summary
        if not success:
            print(f"\n⚠️  SEARCH DEBUG INFO")
            print(f"   Query: {query}")
            print(f"   Error: {error}")
            if raw_response:
                print(f"   Response preview: {raw_response[:200]}...")

    def log_fetch(
        self,
        url: str,
        content_length: int,
        success: bool,
        error: str = None
    ):
        """Log a fetch operation."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "fetch",
            "url": url,
            "content_length": content_length,
            "success": success,
            "error": error
        }

        self.logs.append(log_entry)
        self._save_log()

        if not success:
            print(f"\n⚠️  FETCH DEBUG INFO")
            print(f"   URL: {url}")
            print(f"   Error: {error}")

    def _save_log(self):
        """Save logs to file."""
        log_file = self.log_dir / f"search_debug_{self.current_session}.json"
        with open(log_file, 'w') as f:
            json.dump(self.logs, f, indent=2)

    def generate_summary(self) -> str:
        """Generate a summary of search operations."""
        if not self.logs:
            return "No search operations logged."

        total_searches = sum(1 for log in self.logs if log.get('type') != 'fetch')
        successful_searches = sum(
            1 for log in self.logs
            if log.get('type') != 'fetch' and log.get('success')
        )
        total_results = sum(
            log.get('results_count', 0) for log in self.logs
            if log.get('type') != 'fetch'
        )

        total_fetches = sum(1 for log in self.logs if log.get('type') == 'fetch')
        successful_fetches = sum(
            1 for log in self.logs
            if log.get('type') == 'fetch' and log.get('success')
        )

        summary = f"""
Search Operations Summary
========================
Searches:
  - Total: {total_searches}
  - Successful: {successful_searches}
  - Failed: {total_searches - successful_searches}
  - Total results: {total_results}

Fetches:
  - Total: {total_fetches}
  - Successful: {successful_fetches}
  - Failed: {total_fetches - successful_fetches}

Recent Errors:
"""

        # Add recent errors
        errors = [
            log for log in self.logs[-10:]  # Last 10 logs
            if not log.get('success') and log.get('error')
        ]

        if errors:
            for err in errors:
                if err.get('type') == 'fetch':
                    summary += f"  - FETCH {err.get('url', 'unknown')}: {err.get('error')}\n"
                else:
                    summary += f"  - SEARCH '{err.get('query', 'unknown')}': {err.get('error')}\n"
        else:
            summary += "  - No recent errors\n"

        return summary

    def print_summary(self):
        """Print summary to console."""
        print("\n" + self.generate_summary())


# Global debugger instance
_debugger = None


def get_debugger() -> SearchDebugger:
    """Get the global debugger instance."""
    global _debugger
    if _debugger is None:
        _debugger = SearchDebugger()
    return _debugger

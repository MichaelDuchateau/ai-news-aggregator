"""Configuration management for AI News Aggregator."""

import yaml
from pathlib import Path
from typing import Dict, Any
from src.models import RSSFeed, Website, SearchQuery

DEFAULT_MODEL = "claude-sonnet-4-6"


class Config:
    """Configuration manager."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                "Please copy config/config.example.yaml to config/config.yaml and configure it."
            )
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value
    
    def get_rss_feeds(self) -> list[RSSFeed]:
        """Get configured RSS feeds."""
        feeds_data = self.get('sources.rss_feeds', [])
        return [RSSFeed(**feed) for feed in feeds_data]
    
    def get_websites(self) -> list[Website]:
        """Get configured websites."""
        sites_data = self.get('sources.websites', [])
        return [Website(**site) for site in sites_data]
    
    def get_search_queries(self) -> list[SearchQuery]:
        """Get configured search queries."""
        queries_data = self.get('sources.search_queries', [])
        return [SearchQuery(**query) for query in queries_data]
    
    def get_obsidian_vault_path(self) -> Path:
        """Get Obsidian vault path."""
        path_str = self.get('obsidian.vault_path')
        if not path_str or path_str == "/path/to/your/obsidian/vault":
            raise ValueError(
                "Please configure your Obsidian vault path in config/config.yaml"
            )
        return Path(path_str).expanduser()
    
    def get_model(self) -> str:
        """Get the Claude model ID to use."""
        return self.get('model', DEFAULT_MODEL)

    def get_scoring_weights(self) -> Dict[str, float]:
        """Get scoring weights."""
        return self.get('scoring.weights', {})
    
    def get_high_value_keywords(self) -> list[str]:
        """Get high value keywords for scoring."""
        return self.get('scoring.keywords_high_value', [])
    
    def get_medium_value_keywords(self) -> list[str]:
        """Get medium value keywords for scoring."""
        return self.get('scoring.keywords_medium_value', [])

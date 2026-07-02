#!/usr/bin/env python3
"""
AI News Aggregator - Main Entry Point

Orchestrates the weekly AI news discovery, curation, and presentation workflow.
"""

import sys
import argparse

from src.config import Config
from src.state_manager import StateManager
from src.discovery import NewsDiscovery
from src.scoring import NewsScorer
from src.tagger import NewsTagger
from src.obsidian_writer import ObsidianWriter


class AINewsAggregator:
    """Main orchestrator for the AI news aggregation workflow."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        print("🤖 AI News Aggregator")
        print("=" * 50)
        
        try:
            self.config = Config(config_path)
            self.state = StateManager(
                prune_after_weeks=self.config.get('state.archive_after_weeks', 12)
            )
            
            # Initialize components
            self.discovery = NewsDiscovery(self.config, self.state)
            self.scorer = NewsScorer(self.config)
            self.tagger = NewsTagger(self.config)
            self.obsidian = ObsidianWriter(self.config)

            print("✅ Initialized successfully\n")
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            sys.exit(1)
    
    def run_scan_only(self):
        """Run discovery and scanning only."""
        print("Running discovery and scan only...\n")
        
        self.state.init_new_week()
        items = self.discovery.discover_all()
        
        if items:
            items = self.scorer.score_all(items)
            min_tag_score = self.config.get('selection.min_score', 40)
            self.tagger.tag_all(items, min_score=min_tag_score)

            for item in items:
                self.state.mark_url_processed(item.url, "scanned", item.week)
                self.state.add_discovered_url(item.url)
            
            self.obsidian.export_scanned_items(items)
            print(f"\n✅ Scanned {len(items)} items and exported to Obsidian")

        print("\nRun 'streamlit run streamlit_app.py' to review and deep-dive.")

    def show_status(self):
        """Show current workflow status."""
        print(self.state.get_status_summary())


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="AI News Aggregator - Discover, curate, and analyze AI news",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                  Discover, score, tag, and export to Obsidian
  python main.py --status         Show current workflow status
  python main.py --config custom.yaml  Use custom config file
        """
    )

    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current workflow status and exit'
    )

    args = parser.parse_args()

    try:
        aggregator = AINewsAggregator(config_path=args.config)

        if args.status:
            aggregator.show_status()
        else:
            aggregator.run_scan_only()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

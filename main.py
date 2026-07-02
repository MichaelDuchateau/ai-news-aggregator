#!/usr/bin/env python3
"""
AI News Aggregator - Main Entry Point

Orchestrates the weekly AI news discovery, curation, and presentation workflow.
"""

import sys
import argparse
from pathlib import Path

from src.config import Config
from src.state_manager import StateManager
from src.discovery import NewsDiscovery
from src.scoring import NewsScorer
from src.tagger import NewsTagger
from src.obsidian_writer import ObsidianWriter
from src.web_ui import ReviewUI
from src.researcher import Researcher
from src.content_creator import ContentCreator


class AINewsAggregator:
    """Main orchestrator for the AI news aggregation workflow."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        print("🤖 AI News Aggregator")
        print("=" * 50)
        
        try:
            self.config = Config(config_path)
            self.state = StateManager()
            
            # Initialize components
            self.discovery = NewsDiscovery(self.config, self.state)
            self.scorer = NewsScorer(self.config)
            self.tagger = NewsTagger(self.config)
            self.obsidian = ObsidianWriter(self.config)
            self.researcher = Researcher(self.config, self.discovery)
            self.content_creator = ContentCreator(self.config)
            
            print("✅ Initialized successfully\n")
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            sys.exit(1)
    
    def run_full_workflow(self):
        """Execute the complete weekly workflow."""
        print("Starting full weekly workflow...\n")
        
        # Stage 1: Discovery
        print("\n" + "=" * 50)
        print("STAGE 1: DISCOVERY")
        print("=" * 50)
        
        self.state.init_new_week()
        items = self.discovery.discover_all()
        
        if not items:
            print("❌ No items discovered. Check your sources.")
            return
        
        # Stage 2: Scoring and Tagging
        print("\n" + "=" * 50)
        print("STAGE 2: SCORING & TAGGING")
        print("=" * 50)
        
        items = self.scorer.score_all(items)
        min_tag_score = self.config.get('selection.min_score', 40)
        self.tagger.tag_all(items, min_score=min_tag_score)

        # Stage 3: Export All to Obsidian
        print("\n" + "=" * 50)
        print("STAGE 3: EXPORT TO OBSIDIAN")
        print("=" * 50)
        
        for item in items:
            self.state.mark_url_processed(item.url, "scanned", item.week)
            self.state.add_discovered_url(item.url)
        
        self.obsidian.export_scanned_items(items)
        self.state.update_stage("scoring_complete")
        
        # Stage 4: Manual Review
        print("\n" + "=" * 50)
        print("STAGE 4: MANUAL REVIEW")
        print("=" * 50)
        
        shortlist_size = self.config.get('selection.shortlist_size', 10)
        shortlist = self.scorer.get_shortlist(items, shortlist_size)
        
        print(f"\n📋 Top {len(shortlist)} items for review:")
        for i, item in enumerate(shortlist, 1):
            print(f"  {i}. {item.title[:60]}... (Score: {item.score:.1f})")
        
        # Launch web UI for selection
        ui_host = self.config.get('web_ui.host', '127.0.0.1')
        ui_port = self.config.get('web_ui.port', 5000)
        
        review_ui = ReviewUI(host=ui_host, port=ui_port)
        deep_dive_count = self.config.get('selection.deep_dive_count', 3)
        selected_items = review_ui.review(shortlist, deep_dive_count)
        
        if not selected_items:
            print("❌ No items selected. Exiting.")
            return
        
        # Mark selected items
        for item in selected_items:
            self.state.add_shortlisted_url(item.url)
        
        self.state.update_stage("review_complete")
        
        # Stage 5: Deep Dive Research
        print("\n" + "=" * 50)
        print("STAGE 5: DEEP DIVE RESEARCH")
        print("=" * 50)
        
        deep_dive_items = self.researcher.deep_dive_all(selected_items)
        
        # Update Obsidian with deep dive content
        for item in deep_dive_items:
            self.state.add_deep_dive_url(item.url)
            self.state.mark_url_processed(item.url, "deep-dive", item.week)
            self.obsidian.export_deep_dive(item)
        
        self.state.update_stage("deep_dive_complete")
        
        # Stage 6: Create Presentation
        print("\n" + "=" * 50)
        print("STAGE 6: PRESENTATION CREATION")
        print("=" * 50)
        
        output_dir = Path("output") / self.state.get_current_week()
        presentation_file = self.content_creator.create_presentation(
            deep_dive_items,
            self.state.get_current_week(),
            output_dir
        )
        
        if presentation_file:
            print(f"\n🎉 Presentation created: {presentation_file}")
        
        # Update Obsidian notes with presentation info
        for item in deep_dive_items:
            self.obsidian.export_deep_dive(item)
        
        self.state.update_stage("complete")
        
        # Summary
        print("\n" + "=" * 50)
        print("WORKFLOW COMPLETE")
        print("=" * 50)
        print(self.state.get_status_summary())
        print(f"\n📁 Check your Obsidian vault: {self.config.get_obsidian_vault_path()}")
        if presentation_file:
            print(f"📊 Presentation: {presentation_file}")
    
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
  python main.py                  Run full weekly workflow
  python main.py --scan-only      Discover and scan items only
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
        '--scan-only',
        action='store_true',
        help='Run discovery and scanning only (no review or deep dive)'
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
        elif args.scan_only:
            aggregator.run_scan_only()
        else:
            aggregator.run_full_workflow()
    
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

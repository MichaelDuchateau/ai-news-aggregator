# AI News Aggregator

A Claude Code application that automatically discovers, curates, and analyzes AI news weekly. Creates presentation slides and exports structured notes to Obsidian.

## Features

- 🔍 **Automated Discovery**: Scans RSS feeds, websites, and search queries for AI news
- 🏷️ **Smart Tagging**: Auto-generates up to 8 relevant tags per article
- ✅ **Manual Curation**: Simple web UI for selecting deep dive candidates
- 📊 **Scoring System**: Ranks articles based on configurable criteria
- 📝 **Deep Research**: Multi-source analysis for selected articles
- 🎯 **Presentation Generation**: Creates minimal, narration-ready slides
- 📚 **Obsidian Integration**: Exports all content with structured YAML frontmatter

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your settings
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your preferences
```

## Configuration

Edit `config/config.yaml`:

1. Set your Obsidian vault path
2. Customize news sources (RSS feeds, websites, search queries)
3. Adjust scoring criteria weights
4. Configure selection parameters

## Usage

### Full Weekly Run

```bash
python main.py
```

This will:
1. Discover news from configured sources
2. Score and export all items to Obsidian
3. Launch web UI for manual selection
4. Perform deep dives on selected items
5. Generate presentation slides

### Individual Commands

```bash
# Just discover and scan
python main.py --scan-only

# Review previous week's shortlist
python main.py --review

# Generate slides from existing deep dives
python main.py --slides-only
```

## Workflow

```
┌─────────────────┐
│  Discovery      │ Automated: Fetch from all sources
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Scoring        │ Automated: Rank and tag all items
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Export All     │ Automated: Save to Obsidian as "scanned"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Web UI Review  │ MANUAL: Select 3 for deep dive
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Deep Dive      │ Automated: Research selected items
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create Slides  │ Automated: Generate presentation
└─────────────────┘
```

## Project Structure

```
ai-news-aggregator/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── config/
│   ├── config.yaml           # Your settings
│   └── config.example.yaml   # Template
├── src/
│   ├── discovery.py          # News fetching
│   ├── scoring.py            # Ranking logic
│   ├── tagger.py             # Tag generation
│   ├── researcher.py         # Deep dive logic
│   ├── content_creator.py    # Slide generation
│   ├── obsidian_writer.py    # Vault integration
│   └── web_ui.py             # Review interface
├── templates/
│   ├── obsidian_scan.md      # Scanned item template
│   ├── obsidian_deepdive.md  # Deep dive template
│   └── slide_structure.json  # Slide layout
└── state/
    ├── processed_urls.json   # Deduplication
    ├── weekly_state.json     # Current progress
    └── archive/              # Historical data
```

## State Management

The app tracks:
- **processed_urls.json**: Prevents re-scanning same articles
- **weekly_state.json**: Current week's progress and stage
- **archive/**: Historical states for reference

## Obsidian Integration

### Folder Structure

```
Your-Vault/
└── AI-News/
    ├── 2025-W52/
    │   ├── article-1.md
    │   ├── article-2.md
    │   └── ...
    └── 2025-W53/
        └── ...
```

### Note Structure

All notes include:
- YAML frontmatter with metadata
- Auto-generated tags (max 8)
- Source links
- Status tracking (scanned/deep-dive)

## Scheduling

To run weekly:

```bash
# Add to crontab (runs every Monday at 9 AM)
0 9 * * 1 cd /path/to/ai-news-aggregator && python main.py
```

## Tips

- Review scoring criteria after first few weeks
- Add/remove sources based on quality
- Adjust deep dive count if needed
- Customize Obsidian templates to your style

## License

MIT

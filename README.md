# AI News Aggregator

A weekly pipeline that discovers, scores, and curates AI news, then lets you
review and deep-dive candidates in a Streamlit UI before exporting structured
notes to Obsidian and generating narration-ready presentation slides.

## Features

- 🔍 **Automated Discovery**: Scans RSS feeds, websites, and search queries for AI news
- 🏷️ **Smart Tagging**: Auto-generates up to 8 relevant tags per article
- 📊 **Scoring System**: Ranks articles based on configurable criteria
- ✅ **Manual Curation**: Streamlit UI for reviewing the shortlist and picking deep-dive candidates
- 📝 **Deep Research**: Multi-source analysis for selected articles
- 🎯 **Presentation Generation**: Creates minimal, narration-ready slides
- 📚 **Obsidian Integration**: Exports all content with structured YAML frontmatter

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your settings
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your preferences (vault path, model, sources)

# Set your Anthropic API key
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY, or export it directly
```

## Configuration

Edit `config/config.yaml`:

1. Set your Obsidian vault path (`obsidian.vault_path`)
2. Set the Claude model to use (`model:`) — defaults to `claude-sonnet-4-6` if omitted
3. Customize news sources (RSS feeds, websites, search queries)
4. Adjust scoring criteria weights
5. Configure selection parameters (shortlist size, deep dive count, min score)

## Usage

### Weekly Workflow

```bash
# 1. Discover, score, tag, and export everything to Obsidian
python main.py

# 2. Review the shortlist, pick deep-dive candidates, research, and
#    generate the presentation
streamlit run streamlit_app.py
```

`python main.py` runs discovery → scoring → tagging → Obsidian export for
*all* scanned items (nothing needs to be selected up front). Everything from
manual review onward — shortlist review, deep dive research, and
presentation generation — happens in the Streamlit app.

### Other Commands

```bash
# Check current status
python main.py --status

# Use a different config file
python main.py --config custom.yaml
```

### Scheduling

To run discovery weekly:

```bash
# Add to crontab (runs every Monday at 9 AM)
0 9 * * 1 cd /path/to/ai-news-aggregator && python main.py
```

## Workflow

```
┌─────────────────┐
│  Discovery      │ Automated: Fetch from all sources (python main.py)
└────────┬────────┘
         ▼
┌─────────────────┐
│  Scoring        │ Automated: Rank and tag all items
└────────┬────────┘
         ▼
┌─────────────────┐
│  Export All     │ Automated: Save to Obsidian as "scanned"
└────────┬────────┘
         ▼
┌─────────────────┐
│  Streamlit UI   │ MANUAL: Review shortlist, select deep-dive candidates
└────────┬────────┘
         ▼
┌─────────────────┐
│  Deep Dive      │ Automated: Research selected items
└────────┬────────┘
         ▼
┌─────────────────┐
│  Create Slides  │ Automated: Generate presentation (.pptx)
└─────────────────┘
```

## Project Structure

```
ai-news-aggregator/
├── main.py                    # CLI entry point (discovery → scoring → tagging → export)
├── streamlit_app.py           # Review, deep-dive, and presentation UI
├── requirements.txt           # Dependencies
├── .env.example                # Environment variables template
├── config/
│   ├── config.yaml            # Your settings (gitignored)
│   └── config.example.yaml    # Template
├── src/
│   ├── config.py              # Configuration loader
│   ├── state_manager.py       # Progress tracking, dedup, pruning
│   ├── discovery.py           # News fetching (RSS, websites, search)
│   ├── scoring.py             # Ranking logic
│   ├── tagger.py               # Tag generation
│   ├── researcher.py          # Deep dive logic
│   ├── content_creator.py     # Slide generation
│   ├── obsidian_writer.py     # Vault integration
│   ├── web_search_agent.py    # Web search + URL content fetch
│   └── search_debugger.py     # Search operation logging
├── state/
│   ├── processed_urls.json    # Deduplication (pruned after `state.archive_after_weeks`)
│   ├── weekly_state.json      # Current progress
│   ├── search_logs/           # JSON logs of search/fetch operations
│   └── archive/               # Historical weekly state
└── output/
    └── YYYY-WXX/              # Per-week presentation output
```

## State Management

The app tracks:
- **processed_urls.json**: Prevents re-scanning the same articles. Entries older
  than `state.archive_after_weeks` (config, default 12) are pruned on load.
- **weekly_state.json**: Current week's progress and stage.
- **archive/**: Historical weekly states for reference.

## Obsidian Integration

### Folder Structure

```
Your-Vault/
└── AI-News/
    ├── 2026-W01/
    │   ├── article-1.md
    │   ├── article-2.md
    │   └── ...
    └── 2026-W02/
        └── ...
```

### Note Structure

All notes include YAML frontmatter with metadata, auto-generated tags (max 8),
source links, and status tracking (`scanned` / `deep-dive`).

## Debugging Search

Search and URL-fetch operations are logged to `state/search_logs/` as JSON,
one file per process run. Each entry has a timestamp, query/URL, success flag,
error (if any), and a raw response preview. To inspect the most recent run:

```bash
ls -lt state/search_logs/ | head -5
cat state/search_logs/search_debug_*.json | jq '.[] | select(.success == false)'
```

Common issues:
- **No results found**: broaden the query or increase `days_back` in
  `config.yaml`'s `search_queries`.
- **Authentication error**: make sure `ANTHROPIC_API_KEY` is set (`echo $ANTHROPIC_API_KEY`).
- **Parsing failed / fallback extraction used**: Claude's response didn't match
  the expected `TITLE:`/`URL:`/`SUMMARY:` format; check
  `_parse_search_response()` in `src/web_search_agent.py`.

## Testing

```bash
pip install pytest
pytest -q
```

Tests don't call any external API. `scripts/smoke_search.py` is a manual,
live-API smoke script for the search agent — run it directly if you want to
sanity check search behavior against the real API.

## Tips

- Review scoring criteria after the first few weeks.
- Add/remove sources based on quality.
- Adjust deep dive count if needed.
- Customize Obsidian templates in `src/obsidian_writer.py` to your style.

## License

MIT

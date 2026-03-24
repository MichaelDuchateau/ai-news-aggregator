# Project Structure

```
ai-news-aggregator/
│
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick start guide
├── requirements.txt               # Python dependencies
├── setup.sh                       # Setup script
├── main.py                        # Main entry point (executable)
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
│
├── config/                        # Configuration
│   ├── config.example.yaml        # Configuration template
│   └── config.yaml               # Your config (created by setup.sh)
│
├── src/                          # Source code
│   ├── __init__.py               # Package initialization
│   ├── models.py                 # Data models (NewsItem, etc.)
│   ├── config.py                 # Configuration loader
│   ├── state_manager.py          # State tracking
│   ├── discovery.py              # News discovery from sources
│   ├── scoring.py                # Item scoring and ranking
│   ├── tagger.py                 # AI tag generation
│   ├── obsidian_writer.py        # Obsidian export
│   ├── web_ui.py                 # Flask review interface
│   ├── researcher.py             # Deep dive research
│   └── content_creator.py        # Presentation generation
│
├── state/                        # State management (created at runtime)
│   ├── processed_urls.json       # URL deduplication
│   ├── weekly_state.json         # Current week progress
│   └── archive/                  # Historical states
│       └── week_YYYY-WXX.json
│
├── output/                       # Generated content (created at runtime)
│   └── YYYY-WXX/                 # Per-week output
│       ├── AI-News-YYYY-WXX.pptx # Presentation
│       └── slides_html/          # HTML slides (temporary)
│
└── templates/                    # Templates (optional customization)
```

## File Descriptions

### Root Files

- **main.py**: Main orchestrator script. Run this to start the workflow.
- **setup.sh**: Automated setup script for dependencies and configuration.
- **requirements.txt**: Python package dependencies.
- **README.md**: Comprehensive documentation and overview.
- **QUICKSTART.md**: Step-by-step quick start guide.

### Configuration

- **config/config.example.yaml**: Template configuration with all options.
- **config/config.yaml**: Your personal configuration (not version controlled).

### Source Code (`src/`)

All modules follow a clear separation of concerns:

1. **models.py**: Pydantic data models for type safety
2. **config.py**: Configuration management and validation
3. **state_manager.py**: Tracks workflow progress and prevents duplicates
4. **discovery.py**: Fetches news from RSS, websites, and searches
5. **scoring.py**: Ranks items based on configurable criteria
6. **tagger.py**: Generates relevant tags using Claude AI
7. **obsidian_writer.py**: Exports markdown notes with YAML frontmatter
8. **web_ui.py**: Flask-based review interface
9. **researcher.py**: Conducts deep research on selected items
10. **content_creator.py**: Generates presentation slides

### State Management (`state/`)

Automatically created and maintained:

- **processed_urls.json**: Prevents re-processing same articles
- **weekly_state.json**: Current week's progress
- **archive/**: Historical states for reference

### Output (`output/`)

Generated during workflow:

- Organized by week (ISO format: YYYY-WXX)
- Presentations saved as .pptx files
- Temporary HTML slides (can be deleted after conversion)

## Data Flow

```
Config → Discovery → Scoring → Tagging → Obsidian (all items)
                                              ↓
                                         Web UI Review
                                              ↓
                                         Selected Items
                                              ↓
                                         Deep Dive
                                              ↓
                                    Obsidian (updated) + Presentation
```

## Customization Points

1. **Sources**: Edit `config/config.yaml` to add/remove news sources
2. **Scoring**: Adjust weights and keywords in configuration
3. **Tags**: Modify tag categories in configuration
4. **Obsidian Templates**: Customize note structure in `obsidian_writer.py`
5. **Presentation Style**: Adjust slide design in `content_creator.py`

## Dependencies

### Python Packages
- anthropic: Claude AI API
- flask: Web UI framework
- pyyaml: Configuration parsing
- feedparser: RSS feed parsing
- requests: HTTP requests
- beautifulsoup4: HTML parsing
- python-dateutil: Date handling
- pydantic: Data validation
- python-pptx: Presentation creation

### External Requirements
- Python 3.8+
- Internet connection for API calls
- Anthropic API key
- Obsidian vault (local or synced)

## Extending the System

### Adding a New Source Type

1. Add source configuration to `config.example.yaml`
2. Create parser method in `discovery.py`
3. Update `discover_all()` to call new parser

### Customizing Obsidian Notes

Edit templates in `obsidian_writer.py`:
- `_write_scanned_note()` for initial exports
- `_write_deep_dive_note()` for researched items

### Changing Presentation Style

Edit `content_creator.py`:
- Modify HTML templates in `_create_title_slide()` and `_create_item_slide()`
- Adjust CSS in `_create_styles()`
- Customize slide generation in `_add_*_slide_pptx()` methods

## Best Practices

1. **Test configuration**: Run `--scan-only` first to verify setup
2. **Review scoring**: Adjust after first week based on results
3. **Monitor state**: Check `state/weekly_state.json` if issues arise
4. **Backup important data**: Obsidian vault and state files
5. **Update sources**: Regularly review and refresh source list

## Architecture Decisions

### Why Flask for Review?
- Simple, lightweight web UI
- No complex frontend framework needed
- Easy to run locally

### Why python-pptx?
- Reliable Python library for PowerPoint
- No external dependencies
- Works cross-platform

### Why Obsidian?
- Local-first, markdown-based
- Great for knowledge management
- Highly customizable
- Supports backlinking and tags

### Why Weekly Workflow?
- Manageable volume of content
- Time for proper curation
- Aligns with typical review cycles
- Prevents overwhelm

## Performance Notes

- Discovery: ~2-5 minutes (depends on sources)
- Scoring/Tagging: ~1-2 minutes (depends on item count)
- Deep Dive: ~2-3 minutes per item (API intensive)
- Presentation: <1 minute
- Total: ~15-30 minutes per week

## Security Considerations

- API key stored in environment variable (not in code)
- No data sent to third parties (except Anthropic API)
- Local file storage only
- Configuration file excluded from version control
- State files contain only URLs and metadata (no content)

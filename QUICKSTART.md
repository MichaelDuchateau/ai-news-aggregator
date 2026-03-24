# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies

```bash
./setup.sh
```

Or manually:
```bash
pip install -r requirements.txt --break-system-packages
cp config/config.example.yaml config/config.yaml
```

### 2. Configure

Edit `config/config.yaml`:

```yaml
obsidian:
  vault_path: "/Users/yourname/Documents/ObsidianVault"  # CHANGE THIS!
```

### 3. Set API Key

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API key
```

### 4. Run

```bash
python main.py
```

## First Run Walkthrough

1. **Discovery (2-5 minutes)**
   - Scans all configured sources
   - You'll see progress for each source

2. **Scoring & Tagging (1-2 minutes)**
   - Automatically ranks items
   - Generates tags using AI

3. **Export to Obsidian (<1 minute)**
   - All items saved to your vault
   - Check `YourVault/AI-News/YYYY-WXX/`

4. **Manual Review (5-10 minutes)**
   - Web UI opens automatically
   - Review top 10 items
   - Select 3 for deep dive
   - Click checkboxes → "Continue to Deep Dive"

5. **Deep Dive Research (5-10 minutes)**
   - AI researches each selected item
   - Finds related sources
   - Generates narrative stories
   - Updates Obsidian notes

6. **Presentation Creation (<1 minute)**
   - Creates minimal slides for narration
   - Saves to `output/YYYY-WXX/`

## Weekly Usage

### Option 1: Manual Run
```bash
python main.py
```

### Option 2: Scheduled (Cron)
```bash
# Edit crontab
crontab -e

# Add this line (runs every Monday at 9 AM)
0 9 * * 1 cd /path/to/ai-news-aggregator && python3 main.py
```

## Common Commands

```bash
# Full workflow
python main.py

# Just discover and scan (no review)
python main.py --scan-only

# Check status
python main.py --status

# Use different config
python main.py --config my-config.yaml

# Get help
python main.py --help
```

## Customization Tips

### Add More Sources

Edit `config/config.yaml`:

```yaml
sources:
  rss_feeds:
    - url: "https://your-favorite-blog.com/feed"
      name: "My Favorite AI Blog"
      weight: 1.2  # Higher = more important
```

### Adjust Scoring

```yaml
scoring:
  keywords_high_value:
    - "your-keyword"
    - "another-keyword"
  
  weights:
    source_authority: 0.4  # Increase to prioritize trusted sources
    recency: 0.3           # Increase for newer content
```

### Change Deep Dive Count

```yaml
selection:
  shortlist_size: 15  # More items to review
  deep_dive_count: 5  # More deep dives per week
```

## Obsidian Organization

Your vault structure:
```
YourVault/
└── AI-News/
    ├── 2025-W52/
    │   ├── article-1.md
    │   ├── article-2.md
    │   └── ...
    └── 2025-W53/
        └── ...
```

Each note includes:
- YAML frontmatter with metadata
- Auto-generated tags
- Summary and key points
- For deep dives: full narrative story

## Troubleshooting

### "Configuration file not found"
```bash
cp config/config.example.yaml config/config.yaml
```

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY='your-key'
```

### "Can't find python-pptx"
```bash
pip install python-pptx --break-system-packages
```

### Web UI doesn't open
- Check if port 5000 is available
- Manually open: http://127.0.0.1:5000

### No items discovered
- Check your internet connection
- Verify source URLs in config
- Some sources may be temporarily down

## Next Steps

1. **First week**: Run manually, review quality
2. **Adjust config**: Add/remove sources, tune scoring
3. **Automate**: Set up cron job for weekly runs
4. **Customize**: Adjust Obsidian templates, presentation style

## Getting Help

- Check logs for error messages
- Review configuration file
- Ensure all dependencies are installed
- Verify Obsidian vault path exists

Happy news aggregating! 🤖📰

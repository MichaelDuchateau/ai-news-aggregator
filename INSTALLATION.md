# AI News Aggregator - Installation & Usage Guide

## 🎯 Overview

Your AI News Aggregator is ready! This standalone application will:

1. **Discover** AI news from 15+ sources weekly
2. **Score & Tag** items automatically using AI
3. **Export** all items to your Obsidian vault
4. **Present** top items in a web UI for your review
5. **Research** selected items with deep dives
6. **Generate** minimal presentation slides
7. **Update** Obsidian notes with comprehensive narratives

## 📦 What You Have

```
ai-news-aggregator/
├── Complete Python application
├── Configuration management
├── Web-based review interface
├── Obsidian integration
├── AI-powered tagging and research
└── Presentation generation
```

## 🚀 Installation

### Step 1: Prerequisites

Ensure you have:
- Python 3.8 or higher
- pip (Python package manager)
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Obsidian with a vault

### Step 2: Run Setup

Navigate to the project directory and run:

```bash
cd ai-news-aggregator
./setup.sh
```

Or manually:
```bash
pip install -r requirements.txt --break-system-packages
cp config/config.example.yaml config/config.yaml
```

### Step 3: Configure

Edit `config/config.yaml`:

**REQUIRED:**
```yaml
obsidian:
  vault_path: "/path/to/your/obsidian/vault"  # Change this!
```

**OPTIONAL (already configured with good defaults):**
- News sources (RSS feeds, websites, search queries)
- Scoring weights
- Tag categories
- Deep dive settings

### Step 4: Set API Key

**Option A - Environment Variable:**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Option B - .env File:**
```bash
cp .env.example .env
# Edit .env and add your API key
```

**Option C - Add to Shell Profile:**
```bash
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

## 📋 Usage

### First Run (Manual)

```bash
python main.py
```

**What happens:**

1. **Discovery** (2-5 min): Scans all configured sources
2. **Scoring & Tagging** (1-2 min): AI ranks and tags items
3. **Export to Obsidian** (<1 min): All items saved to vault
4. **Web UI Review** (5-10 min): You select 3 items for deep dive
5. **Deep Dive Research** (5-10 min): AI researches selected items
6. **Presentation** (<1 min): Creates slides for narration

**Total time: ~15-30 minutes**

### Web UI Review

When the web UI launches:

1. Browser opens automatically at `http://127.0.0.1:5000`
2. Review top 10 items (sorted by score)
3. Click checkboxes for items you want deep dives on
4. Click "Continue to Deep Dive"
5. Return to terminal (it will continue automatically)

### Weekly Automation

**Option 1: Cron Job (Linux/Mac)**

```bash
crontab -e
```

Add this line (runs every Monday at 9 AM):
```
0 9 * * 1 cd /path/to/ai-news-aggregator && /usr/bin/python3 main.py
```

**Option 2: Manual Weekly Run**

Just run when you want:
```bash
python main.py
```

### Other Commands

```bash
# Just scan and tag (no review or deep dive)
python main.py --scan-only

# Check current status
python main.py --status

# Use custom config
python main.py --config my-config.yaml

# Get help
python main.py --help
```

## 🗂️ Obsidian Integration

### Folder Structure

Your vault will have:
```
YourVault/
└── AI-News/
    ├── 2025-W52/
    │   ├── openai-releases-new-model.md
    │   ├── google-ai-breakthrough.md
    │   └── ...
    └── 2025-W53/
        └── ...
```

### Note Structure

**Scanned Items:**
```markdown
---
title: "Article Title"
source: "Source Name"
url: "https://..."
status: scanned
score: 85.3
tags:
  - ai/llm
  - company/openai
  - type/product
  - impact/high
week: 2025-W52
---

# Article Title

**Source:** [Source Name](url)
**Status:** 🔍 Scanned

## Summary
[Auto-generated summary]

## Key Points
- Point 1
- Point 2

## Tags Rationale
[Why these tags were chosen]
```

**Deep Dive Items:**
```markdown
---
title: "Article Title"
status: deep-dive
slide_file: "AI-News-2025-W52.pptx"
slide_number: 1
---

# Article Title

**Status:** 🔍 Deep Dive

## Executive Summary
[One paragraph]

## The Story
[500-800 word narrative]

## Technical Details
[Key technical points]

## Why This Matters
[Impact analysis]

## Related Sources
[Additional research sources]

## Slide Reference
Presentation: `AI-News-2025-W52.pptx`
Slide: 1
```

## 🎨 Customization

### Adding News Sources

Edit `config/config.yaml`:

```yaml
sources:
  rss_feeds:
    - url: "https://your-blog.com/feed"
      name: "Your Favorite Blog"
      weight: 1.3  # Higher = more important
```

### Adjusting Scoring

```yaml
scoring:
  keywords_high_value:
    - "your-keyword"
    - "important-term"
  
  weights:
    source_authority: 0.35  # Increase for trusted sources
    recency: 0.25
    uniqueness: 0.25
    keyword_match: 0.15
```

### Changing Selection Criteria

```yaml
selection:
  shortlist_size: 15    # More items to review
  deep_dive_count: 5    # More deep dives per week
  min_score: 50         # Higher quality threshold
```

## 🎯 Presentation Slides

Slides are **minimal and visual** (Garr Reynolds philosophy):

- **Title slide**: Week number and branding
- **Content slides**: One per deep dive item
  - Large title
  - Key point or quote (for visual impact)
  - Source attribution
- **Speaker notes**: Full narrative for your narration

**Output location:** `output/YYYY-WXX/AI-News-YYYY-WXX.pptx`

## 🔧 Troubleshooting

### "Configuration file not found"
```bash
cp config/config.example.yaml config/config.yaml
```

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt --break-system-packages
```

### Web UI doesn't open
- Manually open: http://127.0.0.1:5000
- Check if port 5000 is available
- Try different port in config

### No items discovered
- Check internet connection
- Verify source URLs are accessible
- Some sources may be temporarily down

### Obsidian notes not appearing
- Verify vault path in config is correct
- Check folder permissions
- Ensure Obsidian vault is not in use

## 📊 Expected Results

After first run, you'll have:

1. **~30-50 scanned items** in Obsidian (all discovered items)
2. **3 deep dive items** with comprehensive research
3. **1 presentation** with minimal slides for narration
4. **State tracking** to prevent duplicates next week

## 🎓 Tips for Best Results

1. **Week 1**: Run manually, review configuration
2. **Week 2**: Adjust scoring based on quality
3. **Week 3**: Fine-tune sources (add/remove based on value)
4. **Week 4+**: Set up automation, refine to your preferences

### Scoring Calibration

After first run, check scores:
- Items 80-100: Should be high quality, relevant
- Items 60-79: Good but not exceptional
- Items 40-59: Borderline
- Items <40: Filtered out

Adjust weights in config if needed.

### Source Quality

Monitor which sources provide best items:
- High-weight sources (1.3-1.5): Official blogs, research papers
- Medium-weight (1.0-1.2): News sites, aggregators
- Lower sources if they consistently produce low scores

## 🔄 Weekly Workflow

**Recommended:**

1. **Monday morning**: Run aggregator (automated via cron)
2. **Monday afternoon**: Review web UI, select deep dives
3. **Tuesday**: Review Obsidian notes, customize if needed
4. **Wednesday**: Use presentation for team update/personal review

## 📈 Scaling Up

Want more content?

```yaml
selection:
  shortlist_size: 20    # Review more items
  deep_dive_count: 10   # More deep research

deep_dive:
  research_sources: 8   # More sources per item
  narrative_length: [800, 1200]  # Longer narratives
```

**Note:** More items = longer processing time and higher API costs

## 💾 Backup & Maintenance

**What to backup:**
- `config/config.yaml` (your settings)
- `state/` directory (prevents re-processing)
- Obsidian vault (your notes)

**What can be regenerated:**
- `output/` presentations
- Temporary files

**Maintenance:**
- Check `state/archive/` periodically (can delete old weeks)
- Update news sources quarterly
- Review and adjust scoring weights

## 🆘 Getting Help

1. Check the error message carefully
2. Review `state/weekly_state.json` for progress
3. Run with `--status` to see current state
4. Check configuration file syntax
5. Ensure all dependencies installed

## 🎉 You're Ready!

Everything is set up and ready to go. Just run:

```bash
cd ai-news-aggregator
python main.py
```

Enjoy your automated AI news curation system! 🤖📰

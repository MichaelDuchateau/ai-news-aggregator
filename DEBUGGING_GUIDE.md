# Web Search Debugging Guide

Quick reference for troubleshooting web search issues in the AI News Aggregator.

## Quick Diagnostics

### 1. Is the API Key Set?

```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# If empty, set it
export ANTHROPIC_API_KEY='your-api-key-here'

# Or create .env file
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your-key
```

### 2. Test Search Functionality

```bash
# Run the test suite
python3 test_search.py

# Expected output if working:
# ✅ PASS: Basic Search
# ✅ PASS: Fetch Content
# ✅ PASS: LLM Search
```

### 3. Check Recent Search Logs

```bash
# View most recent log
ls -lt state/search_logs/ | head -5

# Check for errors
cat state/search_logs/search_debug_*.json | jq '.[] | select(.success == false)'

# Count successful vs failed searches
echo "Successful:"
cat state/search_logs/search_debug_*.json | jq '[.[] | select(.success == true)] | length'
echo "Failed:"
cat state/search_logs/search_debug_*.json | jq '[.[] | select(.success == false)] | length'
```

## Common Issues

### Issue: "No results found"

**Symptoms:**
- Console shows: `⚠️ No results found`
- Zero items discovered from web search

**Causes & Solutions:**

1. **Query too specific**
   - Try broader search terms
   - Check `config/config.yaml` search queries
   - Example: Change "AI breakthrough December 2025" to "AI breakthrough"

2. **Time range too narrow**
   - Increase `days_back` in search queries
   - Default is 7 days, try 14 or 30

3. **Search tool not invoked**
   - Check debug logs for: `ℹ️ Tool 'web_search' was invoked`
   - If missing, the API might not be using the tool

**Debugging Steps:**
```bash
# Check what query is being sent
grep "Query:" state/search_logs/search_debug_*.json

# Check raw response
cat state/search_logs/search_debug_*.json | jq '.[].raw_response_preview'

# Try manual test
python3 -c "
from src.web_search_agent import WebSearchAgent
agent = WebSearchAgent()
results = agent.search_news('AI news', days_back=30)
print(f'Found {len(results)} results')
"
```

### Issue: "Authentication Error"

**Symptoms:**
```
TypeError: "Could not resolve authentication method..."
```

**Solution:**
```bash
# Set the API key
export ANTHROPIC_API_KEY='your-key-here'

# Verify it's set
env | grep ANTHROPIC

# Or add to .env file
echo "ANTHROPIC_API_KEY=your-key" > .env
```

### Issue: "Parsing Failed"

**Symptoms:**
- Console shows: `ℹ️ Trying fallback URL extraction...`
- Few or no results despite API success

**Causes:**
- Claude returned unstructured response
- Response doesn't match expected format

**Solutions:**

1. **Check response format in logs**
   ```bash
   cat state/search_logs/search_debug_*.json | jq '.[0].raw_response_preview'
   ```

2. **Improve prompt in web_search_agent.py**
   - The agent expects: `TITLE: ... \n URL: ... \n SUMMARY: ...`
   - If format differs, update `_parse_search_response()`

3. **Use fallback parser**
   - Already automatic
   - Extracts any URLs found in text

### Issue: "Fetching Content Failed"

**Symptoms:**
- `❌ Fetch failed` in console
- Deep dive has no content

**Debugging:**
```bash
# Check fetch logs
cat state/search_logs/search_debug_*.json | jq '.[] | select(.type == "fetch")'

# Test manual fetch
python3 -c "
from src.web_search_agent import WebSearchAgent
agent = WebSearchAgent()
content = agent.fetch_url_content('https://openai.com/news')
print(f'Fetched {len(content)} chars')
print(content[:200])
"
```

## Monitoring Search Health

### Real-time Monitoring

While running the main application, watch for these indicators:

**Good Signs:**
- `✅ Found X results` with X > 0
- `Top results:` section lists articles
- No warning or error messages

**Warning Signs:**
- `⚠️ No results found` repeatedly
- `ℹ️ Trying fallback URL extraction...` often
- `ℹ️ Filtered out X already-processed URLs` with high X

**Error Signs:**
- `❌ Search failed`
- `❌ Fetch failed`
- Exception tracebacks

### Post-Run Analysis

After running the application, review the search debugger summary:

```bash
# It's printed at the end of the run, or generate manually:
python3 -c "
from src.search_debugger import get_debugger
debugger = get_debugger()
debugger.print_summary()
"
```

Expected output:
```
Search Operations Summary
========================
Searches:
  - Total: 3
  - Successful: 3
  - Failed: 0
  - Total results: 15
```

## Log File Analysis

### Structure of Log Files

Each entry in `state/search_logs/search_debug_*.json`:

```json
{
  "timestamp": "2025-12-26T21:00:00.000000",
  "query": "AI breakthrough",
  "results_count": 5,
  "success": true,
  "error": null,
  "raw_response_preview": "...",
  "parsed_items": [
    {"title": "...", "url": "..."},
    ...
  ]
}
```

### Useful Queries

```bash
# Get all failed searches
jq '.[] | select(.success == false)' state/search_logs/search_debug_*.json

# Get searches with no results
jq '.[] | select(.results_count == 0)' state/search_logs/search_debug_*.json

# Get average results per search
jq '[.[] | .results_count] | add / length' state/search_logs/search_debug_*.json

# Get most recent error
jq '.[] | select(.error != null) | .error' state/search_logs/search_debug_*.json | tail -1
```

## Configuration Tuning

### Adjusting Search Queries

Edit `config/config.yaml`:

```yaml
search_queries:
  # Make queries broader
  - query: "AI breakthrough OR artificial intelligence breakthrough"
    days_back: 14  # Increase time range
    min_relevance: 0.6  # Lower threshold

  # Add more specific queries
  - query: "GPT OR Claude OR Gemini new release"
    days_back: 7
    min_relevance: 0.8
```

### Adjusting Agent Behavior

Edit `src/web_search_agent.py`:

**Increase max_tokens for longer responses:**
```python
max_tokens=4000,  # Change to 6000 for more results
```

**Modify the prompt format:**
```python
content = f"""Search for recent AI news: {query}

Focus on articles from the last {days_back} days.
Return the top {max_results} most relevant results.

For each result, provide...
"""
```

## Testing Changes

After making changes, test them:

```bash
# 1. Test basic functionality
python3 test_search.py

# 2. Test with actual config
python3 main.py --scan-only

# 3. Review logs
cat state/search_logs/search_debug_*.json | jq '.[-5:]'
```

## Performance Optimization

### Reducing API Calls

1. **Increase caching** (future improvement)
2. **Reduce search query count** in config
3. **Increase `days_back`** to get more results per search
4. **Use RSS/website scraping** more than web search

### Improving Result Quality

1. **Refine search queries** to be more specific
2. **Adjust `min_relevance`** threshold
3. **Review and update keyword lists** in scoring config
4. **Manually review shortlist** in web UI

## Getting Help

If issues persist:

1. **Check logs**: `state/search_logs/`
2. **Run tests**: `python3 test_search.py`
3. **Review config**: `config/config.yaml`
4. **Check API status**: https://status.anthropic.com
5. **Verify API key**: Has sufficient credits

## Useful Commands Reference

```bash
# Setup
export ANTHROPIC_API_KEY='your-key'
cp .env.example .env

# Testing
python3 test_search.py
python3 main.py --scan-only

# Monitoring
tail -f state/search_logs/search_debug_*.json
watch -n 5 'ls -lh state/search_logs/'

# Analysis
jq '.' state/search_logs/search_debug_*.json | less
grep -r "ERROR" state/search_logs/
```

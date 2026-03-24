# Web Search Agent Improvements

## Summary

The web search functionality has been refactored into separate, transparent agents to improve debugging and visibility into search operations.

## Changes Made

### 1. New Files Created

#### `src/web_search_agent.py`
A dedicated agent for handling all web search and fetch operations with:
- **Transparent logging**: Each search operation is numbered and shows detailed progress
- **Structured response parsing**: Expects results in `TITLE/URL/SUMMARY` format
- **Fallback parsing**: If structured parsing fails, tries to extract URLs from text
- **Better error messages**: Shows what went wrong and includes response previews
- **Individual operation tracking**: Each search and fetch is logged separately

Key methods:
- `search_news()`: Performs web searches with detailed logging
- `fetch_url_content()`: Fetches content from URLs
- `_parse_search_response()`: Parses Claude's search responses
- `_fallback_url_extraction()`: Backup URL extraction method

#### `src/search_debugger.py`
A debugging and diagnostics module that:
- **Logs all operations**: Saves JSON logs of every search and fetch
- **Tracks success/failure**: Records which operations worked and which failed
- **Generates summaries**: Provides overview of search performance
- **Stores raw responses**: Keeps response previews for debugging

Key features:
- Automatic log file creation in `state/search_logs/`
- JSON format for easy analysis
- Console output for immediate debugging
- Summary statistics

#### `test_search.py`
A comprehensive test suite that:
- Tests basic search functionality
- Tests URL content fetching
- Tests LLM-specific searches
- Generates detailed test reports
- Uses the debugger to show operation details

### 2. Modified Files

#### `src/discovery.py`
- Added `WebSearchAgent` import and initialization
- Replaced inline web search code with agent calls
- Improved error handling and logging
- Better filtering of already-processed URLs

Changes:
```python
# Before: Direct API calls with basic parsing
# After: Uses WebSearchAgent for transparent operations
items = self.search_agent.search_news(
    query=query.query,
    days_back=query.days_back,
    max_results=10
)
```

#### `src/researcher.py`
- Added `WebSearchAgent` import and initialization
- Refactored `_find_related_sources()` to use search agent
- Better error handling with stack traces
- More structured approach to finding related content

Changes:
```python
# Before: Direct API calls
# After: Uses search agent with proper result handling
news_items = self.search_agent.search_news(
    query=search_query,
    days_back=30,
    max_results=5
)
```

### 3. New Directory Structure

```
state/
└── search_logs/          # New directory for search operation logs
    └── search_debug_YYYYMMDD_HHMMSS.json
```

## Benefits

### 1. Transparency
- Every search operation is numbered and tracked
- You can see exactly what query was sent
- You can see what response was received
- You can see how many results were found

### 2. Debugging
- Detailed error messages with full stack traces
- Raw response previews when searches fail
- Persistent logs in JSON format
- Summary statistics for all operations

### 3. Maintainability
- Search logic centralized in one place
- Easier to update search behavior
- Consistent error handling across the codebase
- Clear separation of concerns

### 4. Testing
- Dedicated test suite for search functionality
- Easy to run tests independently
- Clear pass/fail indicators
- Detailed operation logs

## Usage

### Running the Full Application

The application works exactly as before, but now with better logging:

```bash
python3 main.py
```

You'll see improved console output like:
```
  🔎 Search Agent #1
     Query: AI breakthrough OR artificial intelligence breakthrough...
     Time range: Last 7 days
     ✅ Found 3 results
     Top results:
       1. New AI Model Achieves State-of-the-Art Performance...
       2. Breakthrough in Natural Language Understanding...
       3. AI System Passes Professional Certification Exam...
```

### Running Tests

To test search functionality independently:

```bash
# Make sure ANTHROPIC_API_KEY is set
export ANTHROPIC_API_KEY='your-api-key-here'

# Or create .env file
cp .env.example .env
# Edit .env and add your key

# Run tests
python3 test_search.py
```

### Viewing Debug Logs

Search logs are automatically saved to `state/search_logs/`:

```bash
# View the most recent log
ls -lt state/search_logs/ | head -n 2
cat state/search_logs/search_debug_YYYYMMDD_HHMMSS.json
```

Each log entry includes:
- Timestamp
- Query or URL
- Success/failure status
- Error message (if failed)
- Raw response preview
- Parsed results

## Troubleshooting

### No Search Results

If searches return no results, check:

1. **API Key**: Make sure `ANTHROPIC_API_KEY` is set
   ```bash
   echo $ANTHROPIC_API_KEY
   ```

2. **Debug Logs**: Check the search logs for errors
   ```bash
   cat state/search_logs/search_debug_*.json | grep -A 5 '"success": false'
   ```

3. **Console Output**: Look for warning messages in the console
   - "⚠️ No results found" - Query returned no matches
   - "❌ Search failed" - API error occurred

4. **Raw Response**: The agent shows response previews when no results are found
   ```
   ⚠️  No results found
   Response preview: [TextBlock(text='I found these results...'...
   ```

### API Errors

If you see authentication errors:
```bash
# Set the API key
export ANTHROPIC_API_KEY='your-key'

# Or use .env file
echo "ANTHROPIC_API_KEY=your-key" > .env
```

### Parsing Issues

If results are found but not parsed correctly:
- Check the debug logs for raw responses
- The agent uses fallback parsing if structured parsing fails
- Look for "ℹ️ Trying fallback URL extraction..." messages

## Next Steps

### Immediate
1. ✅ Set up ANTHROPIC_API_KEY environment variable
2. ✅ Run test_search.py to verify everything works
3. ✅ Review debug logs to ensure search is functioning

### Optional Improvements
- Add retry logic for failed searches
- Implement caching to reduce API calls
- Add more sophisticated response parsing
- Create visualization for search statistics
- Add search quality metrics

## Technical Details

### Agent Architecture

The `WebSearchAgent` uses Claude's extended context protocol with:
- `web_search_20250305` tool for searching
- `web_fetch` tool for fetching content
- Claude Sonnet 4 model for reliable parsing

### Error Handling Strategy

1. **Try-Catch**: All operations wrapped in try-except
2. **Logging**: Errors logged to both console and files
3. **Fallbacks**: Multiple parsing strategies attempted
4. **Graceful Degradation**: Returns empty results instead of crashing

### Logging Strategy

1. **Console**: Real-time feedback for user
2. **JSON Files**: Persistent logs for debugging
3. **Summary Stats**: Overview of operation success rates
4. **Response Previews**: Raw data when debugging needed

## Example Output

### Successful Search
```
🔎 Search Agent #1
   Query: AI breakthrough December 2025...
   Time range: Last 7 days
   ✅ Found 5 results
   Top results:
     1. Google Releases Gemini 3.0 with Enhanced Reasoning...
     2. New Study Shows AI Surpasses Human Performance in...
     3. OpenAI Announces GPT-5 Beta Program...
```

### Failed Search (with debugging)
```
🔎 Search Agent #1
   Query: obscure_topic_with_no_results...
   Time range: Last 7 days
   ⚠️  No results found
   Response preview: [TextBlock(text='I searched for...
   ℹ️  Trying fallback URL extraction...
   ✅ Found 0 results
```

## Files Modified/Created

### New Files
- `src/web_search_agent.py` (303 lines)
- `src/search_debugger.py` (149 lines)
- `test_search.py` (145 lines)
- `SEARCH_AGENT_IMPROVEMENTS.md` (this file)

### Modified Files
- `src/discovery.py` (3 changes)
- `src/researcher.py` (2 changes)

### Total Changes
- ~600 lines of new code
- Improved error handling
- Better logging throughout
- Comprehensive test coverage

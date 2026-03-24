"""Simple web UI for manually reviewing and selecting news items."""

from flask import Flask, render_template_string, request, jsonify
from typing import List
import webbrowser
import threading

from src.models import NewsItem


class ReviewUI:
    """Web-based UI for reviewing shortlisted items."""
    
    def __init__(self, host='127.0.0.1', port=5000):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.items = []
        self.selected_urls = []
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE, items=self.items)
        
        @self.app.route('/submit', methods=['POST'])
        def submit():
            self.selected_urls = request.json.get('selected', [])
            return jsonify({'status': 'success', 'count': len(self.selected_urls)})
        
        @self.app.route('/status')
        def status():
            return jsonify({'selected_count': len(self.selected_urls)})
    
    def review(self, items: List[NewsItem], deep_dive_count: int = 3) -> List[NewsItem]:
        """
        Launch web UI for reviewing items.
        Returns selected items for deep dive.
        """
        self.items = items
        self.selected_urls = []
        
        print(f"\n📋 Review UI launched at http://{self.host}:{self.port}")
        print(f"   Select {deep_dive_count} items for deep dive")
        print("   Press Ctrl+C when done\n")
        
        # Open browser
        threading.Timer(1.0, lambda: webbrowser.open(f'http://{self.host}:{self.port}')).start()
        
        try:
            # Run Flask app (blocking)
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        except KeyboardInterrupt:
            print("\n✅ Review complete")
        
        # Return selected items
        selected = [item for item in items if item.url in self.selected_urls]
        print(f"   Selected {len(selected)} items for deep dive")
        
        return selected


# HTML template for the review UI
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI News Review</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        
        h1 {
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #718096;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .item {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
        }
        
        .item:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            transform: translateY(-2px);
        }
        
        .item.selected {
            border-color: #667eea;
            background: #f7fafc;
        }
        
        .item-header {
            display: flex;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 12px;
        }
        
        .checkbox {
            width: 24px;
            height: 24px;
            margin-top: 4px;
            cursor: pointer;
            accent-color: #667eea;
        }
        
        .item-content {
            flex: 1;
        }
        
        .item-title {
            font-size: 1.3em;
            color: #2d3748;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .item-meta {
            display: flex;
            gap: 20px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #718096;
            font-size: 0.9em;
        }
        
        .score {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
        }
        
        .item-summary {
            color: #4a5568;
            line-height: 1.6;
            margin-bottom: 12px;
        }
        
        .item-tags {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .tag {
            background: #edf2f7;
            color: #4a5568;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 0.85em;
        }
        
        .actions {
            position: sticky;
            bottom: 20px;
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 30px;
        }
        
        .selection-count {
            font-size: 1.1em;
            color: #4a5568;
        }
        
        .selection-count strong {
            color: #667eea;
            font-size: 1.3em;
        }
        
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 14px 32px;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        button:disabled {
            background: #cbd5e0;
            cursor: not-allowed;
            transform: none;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #718096;
        }
        
        .link {
            color: #667eea;
            text-decoration: none;
        }
        
        .link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 AI News Review</h1>
        <p class="subtitle">Select items for deep dive analysis</p>
        
        {% if items %}
            <div id="items">
                {% for item in items %}
                <div class="item" onclick="toggleItem('{{ item.url }}', this)">
                    <div class="item-header">
                        <input type="checkbox" 
                               class="checkbox" 
                               id="check-{{ loop.index }}"
                               data-url="{{ item.url }}"
                               onclick="event.stopPropagation()">
                        <div class="item-content">
                            <div class="item-title">{{ item.title }}</div>
                            <div class="item-meta">
                                <span class="meta-item">
                                    📰 {{ item.source }}
                                </span>
                                <span class="meta-item score">
                                    Score: {{ "%.1f"|format(item.score) }}
                                </span>
                                <span class="meta-item">
                                    📅 {{ item.discovered.strftime('%Y-%m-%d') }}
                                </span>
                            </div>
                            {% if item.summary %}
                            <div class="item-summary">{{ item.summary[:200] }}...</div>
                            {% endif %}
                            <div class="item-tags">
                                {% for tag in item.tags[:5] %}
                                <span class="tag">{{ tag }}</span>
                                {% endfor %}
                            </div>
                            <div style="margin-top: 8px;">
                                <a href="{{ item.url }}" 
                                   target="_blank" 
                                   class="link"
                                   onclick="event.stopPropagation()">
                                   View article →
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="actions">
                <div class="selection-count">
                    Selected: <strong id="count">0</strong> items
                </div>
                <button onclick="submitSelection()" id="submit-btn">
                    Continue to Deep Dive
                </button>
            </div>
        {% else %}
            <div class="empty-state">
                <h2>No items to review</h2>
                <p>Run the discovery process first.</p>
            </div>
        {% endif %}
    </div>
    
    <script>
        let selected = new Set();
        
        function toggleItem(url, element) {
            const checkbox = element.querySelector('.checkbox');
            checkbox.checked = !checkbox.checked;
            updateSelection(url, checkbox.checked, element);
        }
        
        function updateSelection(url, isSelected, element) {
            if (isSelected) {
                selected.add(url);
                element.classList.add('selected');
            } else {
                selected.delete(url);
                element.classList.remove('selected');
            }
            document.getElementById('count').textContent = selected.size;
        }
        
        // Setup checkbox listeners
        document.querySelectorAll('.checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', function(e) {
                const url = this.dataset.url;
                const item = this.closest('.item');
                updateSelection(url, this.checked, item);
            });
        });
        
        async function submitSelection() {
            if (selected.size === 0) {
                alert('Please select at least one item');
                return;
            }
            
            const btn = document.getElementById('submit-btn');
            btn.disabled = true;
            btn.textContent = 'Processing...';
            
            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        selected: Array.from(selected)
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    btn.textContent = '✓ Selection Saved';
                    setTimeout(() => {
                        alert(`Selection complete! ${data.count} items selected for deep dive.\\n\\nYou can now close this window and return to the terminal.`);
                    }, 500);
                }
            } catch (error) {
                alert('Error submitting selection: ' + error.message);
                btn.disabled = false;
                btn.textContent = 'Continue to Deep Dive';
            }
        }
    </script>
</body>
</html>
'''

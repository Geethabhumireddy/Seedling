# GitHub Issue AI Analyzer

An intelligent GitHub issue classifier and analyzer powered by Google's Gemini AI. Automatically triages issues, suggests labels, and provides actionable insights in seconds.

## Features

- **Intelligent Classification**: Automatically categorizes issues as bugs, feature requests, documentation needs, questions, or other types
- **Priority Assessment**: Assigns numerical priority scores (1-5) with reasoning
- **Smart Label Suggestion**: Recommends relevant labels based on issue content
- **Impact Analysis**: Evaluates potential impact on users and codebase
- **Clean UI**: Responsive, modern interface with visual priority indicators
- **One-Click Analysis**: Simple input of repository URL and issue number

## Quick Start

### Prerequisites
- Python 3.8+
- GitHub account (for API access)
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gitchat
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GITHUB_TOKEN=your_github_token_here  # Optional, for higher rate limits
   ```

### Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. Enter a GitHub repository URL (e.g., `https://github.com/facebook/react`)
2. Provide the issue number you want to analyze
3. Click "Analyze"
4. View results including:
   - Issue summary
   - Classification type
   - Priority score (1-5)
   - Suggested labels
   - Potential impact assessment

### Example
```
Repository: https://github.com/facebook/react
Issue Number: 12345
```

## Architecture

### System Design

The application follows a clean, modular architecture:

```
app.py                 # Streamlit UI and visualization
├── github_utils.py    # GitHub API interaction layer
└── hf.py             # AI analysis engine
```

**Data Flow:**
1. User inputs repository URL and issue number
2. `github_utils.py` fetches issue details and comments from GitHub API
3. Issue data is passed to `hf.py` for AI analysis
4. Gemini API processes the issue with optimized prompt
5. Results displayed in responsive UI with visual indicators

### Edge Case Handling

- **Empty Issue Bodies**: Falls back to title + comments
- **No Comments**: Handles issues with zero discussion gracefully
- **Long Issue Text**: API-level truncation handled transparently
- **Rate Limiting**: GitHub token authentication for higher limits
- **Network Errors**: Comprehensive error messages for debugging
- **Malformed AI Responses**: JSON parsing with fallback error handling

## Prompt Engineering

The AI prompt is carefully designed for reliability:

- **Explicit Format**: Specifies exact JSON structure required
- **Type Categories**: Lists all valid issue types to reduce ambiguity
- **Justification Request**: Asks for reasoning to improve quality
- **No Explanation Requirement**: Forces JSON-only output, avoiding parsing errors
- **Markdown Handling**: Strips code blocks that may wrap JSON

Example prompt structure:
```
"Classify as one of: bug, feature_request, documentation, question, other"
"Priority must be 1-5"
"Return ONLY JSON"
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.40.0 | Web UI framework |
| google-genai | 0.5.1 | Gemini AI API |
| python-dotenv | 1.0.0 | Environment variable management |
| requests | 2.32.3 | HTTP client for GitHub API |

## API Keys Required

### Google Gemini API
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` file as `GEMINI_API_KEY`

### GitHub API Token (Optional)
1. Go to [GitHub Settings → Developer Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Generate new token with `public_repo` scope
3. Add to `.env` file as `GITHUB_TOKEN`

## Performance

- **Analysis Time**: 2-5 seconds per issue
- **API Calls**: 2 per analysis (GitHub fetch + Gemini analysis)
- **Rate Limits**: 
  - GitHub: 60 req/hr (unauthenticated), 5000 req/hr (authenticated)
  - Gemini: Varies by plan

## Going the Extra Mile

- ✅ **Comprehensive Comments**: Every function documented with docstrings
- ✅ **Type Hints**: All parameters and returns annotated
- ✅ **Error Handling**: Graceful fallbacks for all failure modes
- ✅ **JSON Export**: View and copy full analysis as JSON
- ✅ **Visual Feedback**: Real-time spinners and error messages
- ✅ **Modern UI**: Gradient headers, card layouts, color-coded badges
- ✅ **Edge Cases**: Handles empty comments, long text, invalid URLs

## Code Quality Highlights

### Readability
- Clear variable names and logical flow
- Comprehensive docstrings with examples
- Organized file structure

### Robustness
- Type hints for better IDE support
- Exception handling at API boundaries
- Validation of user inputs

### Efficiency
- Direct API calls (no unnecessary overhead)
- Optimized prompt for fastest responses
- Minimal dependencies

## Troubleshooting

### "Failed to fetch GitHub issue"
- Verify repository URL format: `https://github.com/owner/repo`
- Check issue number exists
- Ensure GITHUB_TOKEN is valid if provided

### "Gemini analysis failed"
- Verify GEMINI_API_KEY is set correctly
- Check API key has active quota
- Ensure issue data is not corrupted

### Rate Limiting
- Add GITHUB_TOKEN to `.env` for higher limits
- Implement caching for repeated analyses

## Future Enhancements

- [ ] Analysis caching to reduce API calls
- [ ] Batch processing for multiple issues
- [ ] Custom label templates per repository
- [ ] Historical analysis trends
- [ ] Export reports to PDF/CSV

## License

MIT License - feel free to use this project for educational and commercial purposes.

## Contributing

Contributions welcome! Please ensure:
1. Code includes docstrings and type hints
2. New features are tested
3. Edge cases are handled
4. README is updated

---

Built with ❤️ for developers and maintainers

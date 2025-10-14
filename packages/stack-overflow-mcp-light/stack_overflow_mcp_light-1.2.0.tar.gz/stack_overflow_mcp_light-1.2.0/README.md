# Stack Overflow MCP Server

A Model Context Protocol (MCP) server that provides comprehensive tools for interacting with Stack Overflow through the Stack Exchange API. This server enables AI assistants to search questions, get detailed answers, and explore Stack Overflow content through a standardized interface.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.10.6+-green.svg)](https://github.com/jlowin/fastmcp)

## 🚀 Features

- **Question Search** - Advanced search with multiple filters and sorting options
- **Question Details** - Get comprehensive information including answers with body content
- **Tag-based Search** - Find questions by specific tags
- **Top Answers** - Retrieve highly-voted answers from the community
- **Type Safety** - Full Pydantic validation with structured response models
- **Error Handling** - Comprehensive error reporting and graceful failure modes

## 📦 Installation

### Using uvx (Recommended)

```bash
uvx stack-overflow-mcp-light
```

### Using uv

```bash
uv add stack-overflow-mcp-light
uv run stack-overflow-mcp-light
```

### Using pip

```bash
pip install stack-overflow-mcp-light
stack-overflow-mcp-light
```

## ⚙️ Configuration

### Environment Variables

- **`STACK_EXCHANGE_API_KEY`** (Optional): Stack Exchange API key for increased rate limits. Get one at [Stack Apps](https://stackapps.com/apps/oauth/register)
- **`STACK_OVERFLOW_MCP_SHOW_LOGS`** (Optional): Set to `"true"` to enable detailed logging

> 💡 **API Key**: While optional, an API key significantly increases your rate limits from 300 to 10,000 requests per day.

### Transport Types

1. **`stdio`** (default) - Standard input/output, client launches server automatically
2. **`http`** (recommended for remote) - Modern HTTP transport (aliases: `streamable-http`, `streamable_http`)
3. **`sse`** (legacy) - Server-Sent Events transport (deprecated)

---

## 🚀 Quick Start (uvx)

### Stdio Transport

```json
{
  "mcpServers": {
    "stack-overflow": {
      "command": "uvx",
      "args": ["--no-progress", "stack-overflow-mcp-light"],
      "env": {
        "STACK_EXCHANGE_API_KEY": "your_api_key_here",
        "STACK_OVERFLOW_MCP_SHOW_LOGS": "false"
      }
    }
  }
}
```

### HTTP Transport

**Start server:**
```bash
export STACK_EXCHANGE_API_KEY="your_api_key_here"
uvx --no-progress stack-overflow-mcp-light --transport http --port 8000 --host 0.0.0.0
```

**Client config:**
```json
{
  "mcpServers": {
    "stack-overflow": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

### SSE Transport

**Start server:**
```bash
export STACK_EXCHANGE_API_KEY="your_api_key_here"
uvx --no-progress stack-overflow-mcp-light --transport sse --port 8000 --host 0.0.0.0
```

**Client config:**
```json
{
  "mcpServers": {
    "stack-overflow": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

---

## 🔧 Alternative Commands

### Stdio with `uv run --with`

```json
{
  "mcpServers": {
    "stack-overflow": {
      "command": "uv",
      "args": ["run", "--with", "stack-overflow-mcp-light", "stack-overflow-mcp-light"],
      "env": {
        "STACK_EXCHANGE_API_KEY": "your_api_key_here",
        "STACK_OVERFLOW_MCP_SHOW_LOGS": "false"
      }
    }
  }
}
```

### Stdio with `uv run --directory` (Local Development)

```json
{
  "mcpServers": {
    "stack-overflow": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/stack-overflow-mcp-light", "stack-overflow-mcp-light"],
      "env": {
        "STACK_EXCHANGE_API_KEY": "your_api_key_here",
        "STACK_OVERFLOW_MCP_SHOW_LOGS": "true"
      }
    }
  }
}
```

### Stdio with `pip` Install

```json
{
  "mcpServers": {
    "stack-overflow": {
      "command": "stack-overflow-mcp-light",
      "args": [],
      "env": {
        "STACK_EXCHANGE_API_KEY": "your_api_key_here",
        "STACK_OVERFLOW_MCP_SHOW_LOGS": "false"
      }
    }
  }
}
```

### HTTP/SSE Alternative Commands

All transport types can use these alternative commands:

```bash
# Using uv run --with
export STACK_EXCHANGE_API_KEY="your_api_key_here"
uv run --with stack-overflow-mcp-light stack-overflow-mcp-light --transport http --port 8000

# Using uv run --directory (local development)
export STACK_EXCHANGE_API_KEY="your_api_key_here"
cd /path/to/stack-overflow-mcp-light
uv run stack-overflow-mcp-light --transport http --port 8000

# Using pip install
export STACK_EXCHANGE_API_KEY="your_api_key_here"
stack-overflow-mcp-light --transport http --port 8000
```

## 🛠️ Available Tools

### ❓ Question Tools (3 tools)

#### `search_questions`
Search Stack Overflow questions with advanced filters.
- **Input**: Search parameters including:
  - `q` - Free-form text search
  - `tagged` - Semi-colon delimited list of tags
  - `intitle` - Search in question titles
  - `nottagged` - Exclude these tags
  - `body` - Text in question body
  - `accepted` - Has accepted answer (boolean)
  - `closed` - Question is closed (boolean)
  - `answers` - Minimum number of answers
  - `views` - Minimum view count
  - `sort` - Sort criteria ("activity", "votes", "creation", "hot", "week", "month", "relevance")
  - `order` - Sort order ("asc" or "desc")
  - `page` - Page number (1-25)
  - `page_size` - Items per page (1-100)
- **Output**: Array of question items with essential fields:
  - `question_id` - Question ID
  - `is_answered` - Whether the question has answers
  - `score` - Question score
  - `link` - Link to the question
  - `title` - Question title

#### `fetch_question_answers`
Fetch a specific question, always including answers with body content sorted by the specified criteria.
- **Input**: Question details request including:
  - `question_id` - Question ID (required)
  - `sort` - Answer sort criteria ("activity", "votes", "creation") - defaults to "votes"
  - `order` - Sort order ("asc" or "desc") - defaults to "desc"
  - `page_size` - Maximum number of answers to return (1-100) - defaults to 30
- **Output**: QuestionItem with detailed information including:
  - `question_id` - Question ID
  - `is_answered` - Whether the question has answers
  - `score` - Question score
  - `link` - Link to the question
  - `title` - Question title
  - `answers` - Array of AnswerItem objects with:
    - `answer_id` - Answer ID
    - `is_accepted` - Whether the answer is accepted
    - `score` - Answer score
    - `body` - Answer body content

#### `search_questions_by_tag`
Search questions that have a specific tag.
- **Input**: `tag` (tag name), `sort`, `order`, `page`, `page_size`
- **Output**: Array of question items with essential fields:
  - `question_id` - Question ID
  - `is_answered` - Whether the question has answers
  - `score` - Question score
  - `link` - Link to the question
  - `title` - Question title

## 🧪 Testing

The project includes comprehensive tests covering all tools:

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test categories
uv run pytest tests/test_server.py::TestQuestionTools -v
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/midodimori/stack-overflow-mcp-light.git
cd stack-overflow-mcp-light

# Install with development dependencies
make install-dev

# Run tests
make test

# Format and lint code
make format

# Check code style and types
make lint

# Run the server locally
make run

# See all available commands
make help
```

### Project Structure

```
stack-overflow-mcp-light/
├── src/stack_overflow_mcp_light/
│   ├── __init__.py
│   ├── server.py          # MCP server implementation
│   ├── logging_config.py  # Logging configuration
│   ├── models/            # Pydantic models
│   │   ├── __init__.py
│   │   ├── requests.py    # Request models
│   │   └── responses.py   # Response models
│   └── tools/             # Tool implementations
│       ├── __init__.py
│       ├── base_client.py # Base client for Stack Exchange API
│       └── questions.py   # Question search and retrieval tools
├── tests/
│   ├── test_server.py     # Tool function tests
│   └── test_mcp_integration.py  # MCP integration tests
├── pyproject.toml         # Project configuration
└── README.md
```

## 📚 API Reference

### Question Sort Options
- **activity**: Sort by last activity date (default)
- **votes**: Sort by question score
- **creation**: Sort by creation date
- **hot**: Sort by current hotness
- **week**: Sort by weekly activity
- **month**: Sort by monthly activity
- **relevance**: Sort by search relevance

### Answer Sort Options
- **activity**: Sort by last activity date (default)
- **votes**: Sort by answer score
- **creation**: Sort by creation date

### Sort Order
- **desc**: Descending order (default)
- **asc**: Ascending order

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is provided for educational and informational purposes only. This tool interacts with Stack Overflow's public API and respects their rate limits and terms of service. The authors are not responsible for any misuse of the Stack Exchange API or violation of their terms of service.

## 🔗 Links

- [Stack Overflow](https://stackoverflow.com/)
- [Stack Exchange API Documentation](https://api.stackexchange.com/docs)
- [Stack Apps - API Key Registration](https://stackapps.com/apps/oauth/register)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Claude Desktop](https://claude.ai/desktop)

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the [Stack Overflow Meta](https://meta.stackoverflow.com/) for API-related questions
- Review the comprehensive test suite for usage examples
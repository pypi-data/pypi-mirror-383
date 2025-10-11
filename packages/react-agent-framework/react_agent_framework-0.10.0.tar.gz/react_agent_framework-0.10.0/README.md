# ReAct Agent Framework

> Framework for creating AI agents using the ReAct pattern (Reasoning + Acting) - **FastAPI-style API**

[![Python 3.8+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/react-agent-framework.svg)](https://badge.fury.io/py/react-agent-framework)
[![Downloads](https://pepy.tech/badge/react-agent-framework)](https://pepy.tech/project/react-agent-framework)
[![Tests](https://github.com/marcosf63/react-agent-framework/actions/workflows/test.yml/badge.svg)](https://github.com/marcosf63/react-agent-framework/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://marcosf63.github.io/react-agent-framework/)

## 🤖 What is ReAct?

ReAct (Reasoning + Acting) is an agent pattern that alternates between:
- **Thought (Reasoning)**: Reasoning about what to do
- **Action (Acting)**: Executing an action using available tools
- **Observation**: Analyzing the action result

This cycle continues until the agent has enough information to answer.

## 🚀 Features

- ✅ **FastAPI-style API** - Elegant and intuitive agent creation
- ✅ **Decorator-based tools** - Register functions as tools with `@agent.tool()`
- ✅ **Rich configuration** - Name, description, model, instructions, and more
- ✅ **Interactive CLI** - Built with Typer and Rich
- ✅ **Verbose mode** - Debug agent reasoning step-by-step
- ✅ **Clean Python API** - Minimal code, maximum functionality
- ✅ **Type hints** - Full typing support
- ✅ **Easy to extend** - Create custom tools effortlessly

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key

## 🔧 Installation

### From PyPI (Recommended)

```bash
# Basic installation
pip install react-agent-framework

# With all optional dependencies
pip install react-agent-framework[all]

# With specific providers
pip install react-agent-framework[anthropic]  # Claude support
pip install react-agent-framework[google]     # Gemini support

# With memory backends
pip install react-agent-framework[memory-chroma]  # ChromaDB
pip install react-agent-framework[memory-faiss]   # FAISS

# With MCP support
pip install react-agent-framework[mcp]
```

### From source (Development)

```bash
# Clone the repository
git clone https://github.com/marcosf63/react-agent-framework.git
cd react-agent-framework

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode
pip install -e .

# Configure OpenAI key
cp .env.example .env
# Edit .env file and add your OPENAI_API_KEY
```

## 💻 Usage

### FastAPI-Style API (Recommended)

The framework provides a FastAPI-inspired API for creating agents:

```python
from react_agent_framework import ReactAgent

# Create agent with rich configuration
agent = ReactAgent(
    name="Research Assistant",
    description="An AI assistant for web research",
    model="gpt-4o-mini",
    instructions="You are a helpful research assistant.",
    max_iterations=10
)

# Register tools using decorators (just like FastAPI routes!)
@agent.tool()
def search(query: str) -> str:
    """Search the internet for information"""
    # Your search implementation
    return search_results

@agent.tool()
def calculate(expression: str) -> str:
    """Perform mathematical calculations"""
    result = eval(expression, {"__builtins__": {}}, {})
    return f"Result: {result}"

# Run the agent
answer = agent.run("What is the capital of France?", verbose=True)
print(answer)
```

### CLI (Command Line Interface)

After installation, the `react-agent` command is available:

**Ask a single question:**
```bash
react-agent ask "What is the capital of France?"
```

**Verbose mode (shows reasoning):**
```bash
react-agent ask "What is the capital of France?" --verbose
# or
react-agent ask "What is the capital of France?" -v
```

**Interactive mode:**
```bash
react-agent interactive
# or with verbose
react-agent interactive --verbose
```

**Choose different model:**
```bash
react-agent ask "Search about AI" --model gpt-4
```

**Show version:**
```bash
react-agent version
```

**Help:**
```bash
react-agent --help
react-agent ask --help
```

## 🎯 Agent Configuration

```python
agent = ReactAgent(
    name="Assistant Name",              # Agent name
    description="Agent description",     # What the agent does
    model="gpt-4o-mini",                # OpenAI model
    instructions="Custom instructions",  # Agent system prompt
    temperature=0,                       # Model temperature (0-1)
    max_iterations=10,                   # Max reasoning cycles
    execution_date=datetime.now(),       # Execution timestamp
    api_key="sk-..."                     # OpenAI API key (optional)
)
```

## 🛠️ Creating Custom Tools

Tools are registered using the `@agent.tool()` decorator:

```python
@agent.tool()
def my_tool(input_text: str) -> str:
    """Tool description (used by the agent)"""
    # Your implementation
    return result

# With custom name and description
@agent.tool(name="custom_name", description="Custom description")
def another_tool(data: str) -> str:
    return processed_data
```

## 📁 Project Structure

```
react-agent-framework/
├── react_agent_framework/      # Main package
│   ├── __init__.py            # Public exports
│   ├── core/                  # Framework core
│   │   ├── __init__.py
│   │   └── react_agent.py    # ReactAgent implementation
│   ├── cli/                   # CLI interface
│   │   ├── __init__.py
│   │   └── app.py            # Typer application
│   └── examples/              # Usage examples
│       ├── fastapi_style.py  # FastAPI-style example
│       └── custom_tools.py   # Custom tools example
├── pyproject.toml             # Project configuration
├── setup.py                   # Package setup
├── CHANGELOG.md              # Version history
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## 🔍 How It Works

1. **User asks a question** → "What is the capital of France?"

2. **Agent thinks** → "I need to search for the capital of France"

3. **Agent acts** → Uses the search tool

4. **Agent observes** → Receives: "Paris is the capital of France..."

5. **Agent thinks** → "Now I have the necessary information"

6. **Agent finishes** → "The capital of France is Paris"

## 📚 Examples

### Basic Example

```python
from react_agent_framework import ReactAgent

agent = ReactAgent(name="Assistant")

@agent.tool()
def greet(name: str) -> str:
    """Greet someone"""
    return f"Hello, {name}!"

answer = agent.run("Greet John")
print(answer)  # "Hello, John!"
```

### Advanced Example

See [examples/fastapi_style.py](react_agent_framework/examples/fastapi_style.py) and [examples/custom_tools.py](react_agent_framework/examples/custom_tools.py) for complete examples.

## 🛠️ Development

### Install development dependencies

```bash
pip install -e ".[dev]"
```

### Run examples

```bash
# FastAPI-style example
python -m react_agent_framework.examples.fastapi_style

# Custom tools example
python -m react_agent_framework.examples.custom_tools
```

### Code quality

```bash
# Format code
black react_agent_framework/

# Check linting
ruff check react_agent_framework/

# Type checking
mypy react_agent_framework/ --ignore-missing-imports
```

## 🎯 Use Cases

- 🔍 Research and information analysis
- 🧮 Calculations and data processing
- 🤖 Intelligent virtual assistants
- 📊 Automated analysis and reports
- 🔧 Complex task automation
- 💡 Any application requiring reasoning + action

## ⚙️ API Reference

### ReactAgent

Main class for creating ReAct agents.

**Methods:**
- `tool(name=None, description=None)`: Decorator to register tools
- `run(query, verbose=False)`: Execute agent with a query
- `arun(query, verbose=False)`: Async version (future)
- `clear_history()`: Clear execution history
- `get_tools()`: Get registered tools

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/MyFeature`)
3. Commit your changes (`git commit -m 'Add MyFeature'`)
4. Push to the branch (`git push origin feature/MyFeature`)
5. Open a Pull Request

### Contribution ideas

- Add new built-in tools
- Improve agent prompting
- Add support for other LLMs (Anthropic, Google, etc)
- Implement tests
- Improve documentation
- Create more examples

## 📝 License

This project is under the MIT license. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the paper [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- Built with [OpenAI API](https://openai.com/), [Typer](https://typer.tiangolo.com/), and [Rich](https://rich.readthedocs.io/)
- API design inspired by [FastAPI](https://fastapi.tiangolo.com/)

## 📧 Contact

Marcos - marcosf63@gmail.com

GitHub: https://github.com/marcosf63/react-agent-framework

---

**Built with ❤️ using ReAct Agent Framework**

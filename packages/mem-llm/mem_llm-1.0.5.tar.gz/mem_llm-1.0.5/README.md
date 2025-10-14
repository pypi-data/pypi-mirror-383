# 🧠 mem-llm

**Memory-enabled AI assistant that remembers conversations using local LLMs**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/mem-llm.svg)](https://pypi.org/project/mem-llm/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 What is it?

A lightweight Python library that adds **persistent memory** to local LLM chatbots. Each user gets their own conversation history that the AI remembers across sessions.

**Perfect for:**
- 💬 Customer service chatbots
- 🤖 Personal AI assistants  
- 📝 Context-aware applications
- 🏢 Business automation

---

## ⚡ Quick Start

### 1. Install

```bash
pip install mem-llm
```

### 2. Setup Ollama (one-time)

```bash
# Install: https://ollama.ai/download
ollama serve

# Download model (only 2.5GB)
ollama pull granite4:tiny-h
```

### 3. Use

```python
from mem_llm import MemAgent

# Create agent (one line!)
agent = MemAgent()

# Set user
agent.set_user("john")

# Chat - it remembers!
agent.chat("My name is John")
agent.chat("What's my name?")  # → "Your name is John"
```

---

## 💡 Features

| Feature | Description |
|---------|-------------|
| 🧠 **Memory** | Remembers each user's conversation history |
| 👥 **Multi-user** | Separate memory for each user |
| 🔒 **Privacy** | 100% local, no cloud/API needed |
| ⚡ **Fast** | Lightweight SQLite/JSON storage |
| 🎯 **Simple** | 3 lines of code to get started |

---

## 📖 Usage Examples

### Basic Chat

```python
from mem_llm import MemAgent

agent = MemAgent()
agent.set_user("alice")

# First conversation
agent.chat("I love pizza")

# Later...
agent.chat("What's my favorite food?")
# → "Your favorite food is pizza"
```

### Customer Service Bot

```python
agent = MemAgent()

# Customer 1
agent.set_user("customer_001")
agent.chat("My order #12345 is delayed")

# Customer 2 (different memory!)
agent.set_user("customer_002")
agent.chat("I want to return item #67890")
```

### Check User Profile

```python
# Get automatically extracted user info
profile = agent.get_user_profile()
# {'name': 'Alice', 'favorite_food': 'pizza', 'location': 'NYC'}
```

---

## 🔧 Configuration

### JSON Memory (default - simple)

```python
agent = MemAgent(
    model="granite4:tiny-h",
    use_sql=False,  # Use JSON files
    memory_dir="memories"
)
```

### SQL Memory (advanced - faster)

```python
agent = MemAgent(
    model="granite4:tiny-h",
    use_sql=True,  # Use SQLite
    memory_dir="memories.db"
)
```

### Custom Settings

```python
agent = MemAgent(
    model="llama2",  # Any Ollama model
    ollama_url="http://localhost:11434"
)
```

---

## 📚 API Reference

### MemAgent

```python
# Initialize
agent = MemAgent(model="granite4:tiny-h", use_sql=False)

# Set active user
agent.set_user(user_id: str, name: Optional[str] = None)

# Chat
response = agent.chat(message: str, metadata: Optional[Dict] = None) -> str

# Get profile
profile = agent.get_user_profile(user_id: Optional[str] = None) -> Dict

# System check
status = agent.check_setup() -> Dict
```

---

## 🎨 Advanced: PDF/DOCX Config

Generate config from business documents:

```python
from mem_llm import create_config_from_document

# Create config.yaml from PDF
create_config_from_document(
    doc_path="company_info.pdf",
    output_path="config.yaml",
    company_name="Acme Corp"
)

# Use config
agent = MemAgent(config_file="config.yaml")
```

---

## 🔥 Models

Works with any [Ollama](https://ollama.ai/) model:

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| `granite4:tiny-h` | 2.5GB | ⚡⚡⚡ | ⭐⭐ |
| `llama2` | 4GB | ⚡⚡ | ⭐⭐⭐ |
| `mistral` | 4GB | ⚡⚡ | ⭐⭐⭐⭐ |
| `llama3` | 5GB | ⚡ | ⭐⭐⭐⭐⭐ |

```bash
ollama pull <model-name>
```

---

## 📦 Requirements

- Python 3.8+
- Ollama (for LLM)
- 4GB RAM minimum
- 5GB disk space

**Dependencies** (auto-installed):
- `requests >= 2.31.0`
- `pyyaml >= 6.0.1`

---

## 🐛 Troubleshooting

### Ollama not running?

```bash
ollama serve
```

### Model not found?

```bash
ollama pull granite4:tiny-h
```

### Import error?

```bash
pip install mem-llm --upgrade
```

---

## 📄 License

MIT License - feel free to use in personal and commercial projects!

---

## 🔗 Links

- **PyPI:** https://pypi.org/project/mem-llm/
- **GitHub:** https://github.com/emredeveloper/Mem-LLM
- **Ollama:** https://ollama.ai/

---

## 🌟 Star us on GitHub!

If you find this useful, give us a ⭐ on [GitHub](https://github.com/emredeveloper/Mem-LLM)!

---

<div align="center">
Made with ❤️ by <a href="https://github.com/emredeveloper">C. Emre Karataş</a>
</div>

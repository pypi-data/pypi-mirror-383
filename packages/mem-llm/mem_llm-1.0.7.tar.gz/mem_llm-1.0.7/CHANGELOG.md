# Changelog

All notable changes to this project will be documented in this file.

## [1.0.4] - 2025-10-13

### Added
- ✨ Config-free knowledge base support - KB now works without config.yaml
- ✨ Smart keyword extraction for knowledge base search (Turkish & English stopwords)
- ✨ Enhanced KB context injection - KB data injected directly into user message
- ✨ Automatic user profile extraction (name, favorite_food, location)
- ✨ Turkish language support for profile extraction
- ✨ SQL-JSON memory compatibility methods (`update_user_profile`, `add_user`, `get_statistics` in MemoryManager)
- 📚 New example: `example_knowledge_base.py`
- 🧪 Comprehensive test suite: `comprehensive_test.py`

### Fixed
- 🐛 Knowledge base not being used without config.yaml
- 🐛 LLM ignoring knowledge base information
- 🐛 User profiles returning empty dictionaries
- 🐛 Profile updates not working correctly with SQL memory
- 🐛 Keyword search failing with Turkish queries
- 🐛 Preferences not being parsed from SQL storage

### Improved
- ⚡ Better KB-first response priority in system prompts
- ⚡ More accurate answers from knowledge base
- ⚡ Stronger instruction for using KB data
- ⚡ Enhanced search algorithm with stopword filtering
- 📖 Better documentation and examples

### Changed
- 🔄 KB context now injected into user message (instead of separate system message)
- 🔄 System prompt rewritten for better KB utilization
- 🔄 Profile storage method (preferences stored as JSON in SQL)

## [1.0.3] - 2025-10-12

### Added
- 📦 Initial PyPI release
- 🎯 Core memory features (JSON & SQL)
- 🤖 Ollama integration
- 💾 Knowledge base system
- 🛠️ User tools
- ⚙️ Configuration management

### Features
- Memory-enabled AI agent
- JSON and SQL memory backends
- Knowledge base integration
- User profile management
- Conversation history
- Configuration from YAML/documents

## [1.0.2] - 2025-10-11

### Internal
- 🔧 Package structure improvements
- 📝 Documentation updates

## [1.0.1] - 2025-10-10

### Fixed
- 🐛 Import errors after package rename
- 📦 Package directory naming issues

## [1.0.0] - 2025-10-09

### Initial Release
- 🎉 First stable release
- 🤖 Memory-enabled AI assistant
- 💾 JSON memory management
- 🔌 Ollama integration

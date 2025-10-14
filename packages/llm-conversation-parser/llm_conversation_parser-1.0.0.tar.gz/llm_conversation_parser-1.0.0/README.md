# LLM Conversation Parser

A Python library for parsing LLM conversation JSON files into RAG-optimized format.

## Documentation

- **[Korean Documentation](README_ko.md)** - Detailed documentation for Korean users
- **[LLM JSON Format Guide](LLM_JSON_FORMATS.md)** - Claude, ChatGPT, Grok JSON file structure analysis

## Supported LLMs

- **Claude** (Anthropic)
- **ChatGPT** (OpenAI)
- **Grok** (xAI)

## Installation

```bash
pip install llm-conversation-parser
```

## Quick Start

```python
from llm_conversation_parser import LLMConversationParser

# Initialize parser
parser = LLMConversationParser()

# Parse single file (auto-detect LLM type)
data = parser.parse_file("claude_conversations.json")
print(f"Parsed {len(data)} conversations")

# Parse multiple files
all_data = parser.parse_multiple_files([
    "claude_conversations.json",
    "gpt_conversations.json",
    "grok_conversations.json"
])

# Save parsed data
parser.save_parsed_data_by_llm(all_data, "parsed_data")
```

## Key Features

- **Automatic LLM Detection**: Analyzes JSON structure to determine LLM type
- **Unified Output Format**: Converts all LLM formats to standardized RAG-optimized structure
- **Batch Processing**: Process multiple files at once
- **Error Handling**: Robust error handling with detailed error messages
- **Zero Dependencies**: Uses only Python standard library
- **CLI Support**: Command-line interface included

## Output Format

```json
[
  {
    "id": "message_uuid",
    "content": {
      "user_query": "User's question",
      "conversation_flow": "[AI_ANSWER] Previous AI response\n[USER_QUESTION] User's question"
    },
    "metadata": {
      "previous_ai_answer": "Previous AI response or null",
      "conversation_id": "conversation_uuid"
    }
  }
]
```

## Usage Examples

### 1. Automatic LLM Type Detection

```python
from llm_conversation_parser import LLMConversationParser

parser = LLMConversationParser()

# Automatically detect LLM type based on JSON structure
claude_data = parser.parse_file("my_conversations.json")  # Auto-detected as Claude
gpt_data = parser.parse_file("chat_history.json")       # Auto-detected as ChatGPT
grok_data = parser.parse_file("ai_chat.json")          # Auto-detected as Grok
```

### 2. Explicit LLM Type Specification

```python
# Specify LLM type explicitly
claude_data = parser.parse_file("conversations.json", "claude")
gpt_data = parser.parse_file("conversations.json", "gpt")
grok_data = parser.parse_file("conversations.json", "grok")
```

### 3. Batch Processing

```python
# Process multiple files at once
files = [
    "claude_conversations.json",
    "gpt_conversations.json",
    "grok_conversations.json"
]

# Process all files with auto-detection
data_by_llm = parser.parse_multiple_files(files)

# Check results
for llm_type, conversations in data_by_llm.items():
    print(f"{llm_type}: {len(conversations)} conversations")

# Save by LLM type
parser.save_parsed_data_by_llm(data_by_llm, "parsed_data")
```

### 4. RAG Data Utilization

```python
# Use parsed data for RAG systems
for conversation in data:
    message_id = conversation["id"]
    user_query = conversation["content"]["user_query"]
    conversation_flow = conversation["content"]["conversation_flow"]

    # Extract text for vectorization
    rag_text = f"{user_query}\n{conversation_flow}"

    # Store in vector database
    # vector_db.add_document(message_id, rag_text)
```

## Command Line Interface

```bash
# Parse single file
llm-conversation-parser parse input.json

# Parse multiple files
llm-conversation-parser parse file1.json file2.json --output parsed_data/

# Auto-detect LLM type
llm-conversation-parser parse conversations.json

# Specify LLM type explicitly
llm-conversation-parser parse conversations.json --llm-type claude
```

## License

MIT License

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed changelog.

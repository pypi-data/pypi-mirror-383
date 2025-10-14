# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-10-13

### Added

- Initial release of LLM Conversation Parser
- Support for Claude, ChatGPT, and Grok conversation formats
- Auto-detection of LLM type from JSON structure
- RAG-optimized output format
- Command-line interface
- Batch processing capabilities
- Comprehensive test suite
- Type hints and documentation

### Features

- **Auto LLM Detection**: Automatically detects LLM type from JSON structure
- **Unified Output Format**: Converts all LLM formats to standardized RAG-optimized structure
- **Batch Processing**: Process multiple files at once
- **Error Handling**: Robust error handling with detailed messages
- **No Dependencies**: Uses only Python standard library
- **CLI Support**: Command-line interface for easy usage
- **Type Safety**: Full type hints and mypy support

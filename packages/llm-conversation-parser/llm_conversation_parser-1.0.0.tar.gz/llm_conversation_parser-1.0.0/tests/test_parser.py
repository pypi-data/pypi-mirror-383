"""
Tests for LLM Conversation Parser
"""

import json
import pytest
import tempfile
import os
from llm_conversation_parser import LLMConversationParser


class TestLLMConversationParser:
    """Test cases for LLMConversationParser"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = LLMConversationParser()

    def test_claude_detection(self):
        """Test Claude JSON structure detection"""
        claude_data = [
            {
                "uuid": "test-uuid",
                "name": "Test Conversation",
                "summary": "",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "account": {"uuid": "account-uuid"},
                "chat_messages": [
                    {"uuid": "msg-uuid", "text": "Hello"}
                ]
            }
        ]

        detected_type = self.parser._detect_llm_type(claude_data)
        assert detected_type == "claude"

    def test_gpt_detection(self):
        """Test ChatGPT JSON structure detection"""
        gpt_data = [
            {
                "title": "Test Conversation",
                "create_time": 1234567890,
                "update_time": 1234567890,
                "mapping": {
                    "client-created-root": {
                        "id": "client-created-root",
                        "message": None,
                        "parent": None,
                        "children": []
                    }
                }
            }
        ]

        detected_type = self.parser._detect_llm_type(gpt_data)
        assert detected_type == "gpt"

    def test_grok_detection(self):
        """Test Grok JSON structure detection"""
        grok_data = {
            "conversations": [
                {
                    "conversation": {
                        "id": "conv-id",
                        "title": "Test Conversation"
                    },
                    "responses": [
                        {
                            "response": {
                                "_id": "resp-id",
                                "sender": "human",
                                "message": "Hello"
                            }
                        }
                    ]
                }
            ]
        }

        detected_type = self.parser._detect_llm_type(grok_data)
        assert detected_type == "grok"

    def test_unknown_structure(self):
        """Test unknown JSON structure"""
        unknown_data = {"unknown": "structure"}

        with pytest.raises(ValueError, match="JSON 구조를 분석할 수 없습니다"):
            self.parser._detect_llm_type(unknown_data)

    def test_file_parsing(self):
        """Test file parsing with temporary files"""
        # Create temporary Claude JSON file
        claude_data = [
            {
                "uuid": "test-uuid",
                "name": "Test Conversation",
                "summary": "",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "account": {"uuid": "account-uuid"},
                "chat_messages": [
                    {"uuid": "msg-uuid", "text": "Hello"}
                ]
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                        delete=False) as f:
            json.dump(claude_data, f)
            temp_file = f.name

        try:
            # Test auto-detection
            result = self.parser.parse_file(temp_file)
            assert len(result) == 1
            assert result[0]["id"] == "msg-uuid"
            assert result[0]["content"]["user_query"] == "Hello"

            # Test explicit type
            result2 = self.parser.parse_file(temp_file, "claude")
            assert len(result2) == 1

        finally:
            os.unlink(temp_file)

    def test_multiple_files_parsing(self):
        """Test multiple files parsing"""
        # Create temporary files
        claude_data = [
            {
                "uuid": "test-uuid",
                "name": "Test Conversation",
                "summary": "",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "account": {"uuid": "account-uuid"},
                "chat_messages": [
                    {"uuid": "msg-uuid", "text": "Hello"}
                ]
            }
        ]

        temp_files = []
        try:
            # Create two identical files
            for i in range(2):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                                delete=False) as f:
                    json.dump(claude_data, f)
                    temp_files.append(f.name)

            # Test multiple files parsing
            result = self.parser.parse_multiple_files(temp_files)
            assert "claude" in result
            # Two files, one conversation each
            assert len(result["claude"]) == 2

        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)

    def test_save_parsed_data(self):
        """Test saving parsed data"""
        test_data = [
            {
                "id": "test-id",
                "content": {
                    "user_query": "Test question",
                    "conversation_flow": "[USER_QUESTION] Test question"
                },
                "metadata": {
                    "previous_ai_answer": None,
                    "conversation_id": "conv-id"
                }
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_output.json")
            self.parser.save_parsed_data(test_data, output_path)

            # Verify file was created and contains correct data
            assert os.path.exists(output_path)
            with open(output_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            assert saved_data == test_data
# LLM 대화내역 파서

LLM 대화내역 JSON 파일을 RAG 최적화 형태로 파싱하는 Python 라이브러리입니다.

## 문서

- **[English Documentation](README.md)** - Detailed documentation for English users
- **[LLM JSON 형식 가이드](LLM_JSON_FORMATS.md)** - Claude, ChatGPT, Grok JSON 파일 구조 분석

## 지원 LLM

- **Claude** (Anthropic)
- **ChatGPT** (OpenAI)
- **Grok** (xAI)

## 설치

```bash
pip install llm-conversation-parser
```

## 빠른 시작

```python
from llm_conversation_parser import LLMConversationParser

# 파서 초기화
parser = LLMConversationParser()

# 단일 파일 파싱 (자동 LLM 타입 감지)
data = parser.parse_file("claude_conversations.json")
print(f"파싱된 대화 수: {len(data)}")

# 여러 파일 파싱
all_data = parser.parse_multiple_files([
    "claude_conversations.json",
    "gpt_conversations.json",
    "grok_conversations.json"
])

# LLM별로 분리하여 저장
parser.save_parsed_data_by_llm(all_data, "parsed_data")
```

## 주요 기능

- **자동 LLM 감지**: JSON 구조를 분석하여 LLM 타입을 자동 판단
- **통일된 출력 형식**: 모든 LLM 형식을 표준화된 RAG 최적화 구조로 변환
- **배치 처리**: 여러 파일을 한번에 처리
- **에러 처리**: 상세한 에러 메시지와 함께 견고한 에러 처리
- **의존성 없음**: Python 표준 라이브러리만 사용
- **CLI 지원**: 명령줄 인터페이스 제공

## 출력 형식

```json
[
  {
    "id": "message_uuid",
    "content": {
      "user_query": "사용자의 질문",
      "conversation_flow": "[AI_ANSWER] 이전 AI 응답\n[USER_QUESTION] 사용자의 질문"
    },
    "metadata": {
      "previous_ai_answer": "이전 AI 응답 또는 null",
      "conversation_id": "conversation_uuid"
    }
  }
]
```

## 명령줄 인터페이스

```bash
# 단일 파일 파싱
llm-conversation-parser parse input.json

# 여러 파일 파싱
llm-conversation-parser parse file1.json file2.json --output parsed_data/

# 자동 LLM 타입 감지
llm-conversation-parser parse conversations.json

# LLM 타입 명시
llm-conversation-parser parse conversations.json --llm-type claude
```

## 사용 예시

### 1. 자동 LLM 타입 감지

```python
from llm_conversation_parser import LLMConversationParser

parser = LLMConversationParser()

# 파일명과 관계없이 JSON 구조로 LLM 타입 자동 감지
claude_data = parser.parse_file("my_conversations.json")  # 자동으로 Claude로 감지
gpt_data = parser.parse_file("chat_history.json")       # 자동으로 ChatGPT로 감지
grok_data = parser.parse_file("ai_chat.json")          # 자동으로 Grok으로 감지
```

### 2. 명시적 LLM 타입 지정

```python
# LLM 타입을 명시적으로 지정
claude_data = parser.parse_file("conversations.json", "claude")
gpt_data = parser.parse_file("conversations.json", "gpt")
grok_data = parser.parse_file("conversations.json", "grok")
```

### 3. 배치 처리

```python
# 여러 파일을 한번에 처리
files = [
    "claude_conversations.json",
    "gpt_conversations.json",
    "grok_conversations.json"
]

# 자동 감지로 모든 파일 처리
data_by_llm = parser.parse_multiple_files(files)

# 결과 확인
for llm_type, conversations in data_by_llm.items():
    print(f"{llm_type}: {len(conversations)}개 대화")

# LLM별로 분리하여 저장
parser.save_parsed_data_by_llm(data_by_llm, "parsed_data")
```

## 개발

```bash
# 개발 의존성 설치
pip install -e ".[dev]"

# 테스트 실행
pytest

# 코드 포맷팅
black llm_conversation_parser/

# 린팅
flake8 llm_conversation_parser/

# 타입 체킹
mypy llm_conversation_parser/
```

## 라이선스

MIT License

## 변경 이력

자세한 변경 이력은 [CHANGELOG.md](CHANGELOG.md)를 참조하세요.

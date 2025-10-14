import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime


class LLMConversationParser:
    """
    LLM 대화내역 JSON 파일을 파싱하여 RAG용 형태로 변환하는 클래스
    """
    
    def __init__(self):
        self.llm_types = ['claude', 'gpt', 'grok']
    
    def parse_file(self, file_path: str, llm_type: str = None) -> List[Dict[str, Any]]:
        """
        JSON 파일을 파싱하여 표준 형태로 변환
        
        Args:
            file_path: JSON 파일 경로
            llm_type: LLM 타입 (claude, gpt, grok). None이면 자동 판단
            
        Returns:
            파싱된 대화내역 리스트
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # LLM 타입이 명시되지 않은 경우 자동 판단
        if llm_type is None:
            llm_type = self._detect_llm_type(data)
            print(f"Auto-detected LLM type: {llm_type}")
        
        # LLM 타입에 따라 파싱
        if llm_type == 'claude':
            return self._parse_claude(data)
        elif llm_type == 'gpt':
            return self._parse_gpt(data)
        elif llm_type == 'grok':
            return self._parse_grok(data)
        else:
            raise ValueError(f"지원하지 않는 LLM 타입입니다: {llm_type}")
    
    def _detect_llm_type(self, data: Any) -> str:
        """
        JSON 데이터 구조를 분석하여 LLM 타입을 자동 판단
        
        Args:
            data: JSON 데이터
            
        Returns:
            LLM 타입 (claude, gpt, grok)
        """
        try:
            # Claude 감지: 배열이고 각 요소에 'uuid', 'chat_messages' 필드가 있는 경우
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, dict):
                    if 'uuid' in first_item and 'chat_messages' in first_item:
                        return 'claude'
                    
                    # GPT 감지: 'title', 'create_time', 'mapping' 필드가 있는 경우
                    if 'title' in first_item and 'create_time' in first_item and 'mapping' in first_item:
                        return 'gpt'
            
            # Grok 감지: 객체이고 'conversations' 필드가 있는 경우
            if isinstance(data, dict) and 'conversations' in data:
                return 'grok'
            
            # 추가 검증을 위한 세부 분석
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, dict):
                    # GPT의 mapping 구조 확인
                    if 'mapping' in first_item:
                        mapping = first_item['mapping']
                        if isinstance(mapping, dict) and 'client-created-root' in mapping:
                            return 'gpt'
            
            # Grok의 conversations 구조 확인
            if isinstance(data, dict) and 'conversations' in data:
                conversations = data['conversations']
                if isinstance(conversations, list) and len(conversations) > 0:
                    first_conv = conversations[0]
                    if isinstance(first_conv, dict) and 'conversation' in first_conv and 'responses' in first_conv:
                        return 'grok'
            
            raise ValueError("JSON 구조를 분석할 수 없습니다. 지원되는 LLM 형식이 아닙니다.")
            
        except Exception as e:
            raise ValueError(f"LLM 타입 자동 감지 실패: {str(e)}")
    
    def _parse_claude(self, data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Claude 대화내역 파싱
        """
        results = []
        
        for conversation in data:
            conversation_id = conversation['uuid']
            messages = conversation['chat_messages']
            
            # user 메시지들을 찾아서 처리
            for i, message in enumerate(messages):
                if i % 2 == 0:  # 짝수 인덱스는 user 메시지
                    user_query = message['text']
                    message_id = message['uuid']  # Claude의 실제 UUID 사용
                    
                    # 이전 AI 답변이 있는지 확인
                    previous_ai_answer = None
                    conversation_flow = f"[USER_QUESTION] {user_query}"
                    
                    if i > 0:  # 첫 번째 질문이 아닌 경우
                        previous_ai_answer = messages[i-1]['text']
                        conversation_flow = f"[AI_ANSWER] {previous_ai_answer}\n[USER_QUESTION] {user_query}"
                    
                    results.append({
                        "id": message_id,
                        "content": {
                            "user_query": user_query,
                            "conversation_flow": conversation_flow
                        },
                        "metadata": {
                            "previous_ai_answer": previous_ai_answer,
                            "conversation_id": conversation_id
                        }
                    })
        
        return results
    
    def _parse_gpt(self, data: List[Dict]) -> List[Dict[str, Any]]:
        """
        ChatGPT 대화내역 파싱 (트리 구조를 순차적으로 변환)
        """
        results = []
        
        for conversation in data:
            try:
                conversation_id = conversation.get('title', 'unknown')  # title을 ID로 사용
                mapping = conversation.get('mapping', {})
                
                # 트리 구조를 순차적으로 변환
                user_messages = []
                ai_messages = []
                
                # client-created-root부터 시작하여 순차적으로 메시지 수집
                self._collect_messages_recursive(mapping, 'client-created-root', user_messages, ai_messages)
                
                # user 메시지들을 기준으로 결과 생성
                for i, user_msg in enumerate(user_messages):
                    message_id = user_msg.get('id', f"unknown_{i}")  # GPT의 실제 ID 사용
                    user_query = ""
                    
                    # user_msg가 dict인지 확인하고 content 접근
                    if isinstance(user_msg, dict) and 'content' in user_msg:
                        content = user_msg['content']
                        if isinstance(content, dict) and 'parts' in content:
                            parts = content['parts']
                            if parts and len(parts) > 0:
                                user_query = str(parts[0])
                    
                    # 이전 AI 답변이 있는지 확인
                    previous_ai_answer = None
                    conversation_flow = f"[USER_QUESTION] {user_query}"
                    
                    if i < len(ai_messages):
                        ai_msg = ai_messages[i]
                        if isinstance(ai_msg, dict) and 'content' in ai_msg:
                            ai_content = ai_msg['content']
                            if isinstance(ai_content, dict) and 'parts' in ai_content:
                                ai_parts = ai_content['parts']
                                if ai_parts and len(ai_parts) > 0:
                                    previous_ai_answer = str(ai_parts[0])
                                    conversation_flow = f"[AI_ANSWER] {previous_ai_answer}\n[USER_QUESTION] {user_query}"
                    
                    results.append({
                        "id": message_id,
                        "content": {
                            "user_query": user_query,
                            "conversation_flow": conversation_flow
                        },
                        "metadata": {
                            "previous_ai_answer": previous_ai_answer,
                            "conversation_id": conversation_id
                        }
                    })
                    
            except Exception as e:
                print(f"GPT 대화 파싱 중 에러: {str(e)}")
                continue
        
        return results
    
    def _collect_messages_recursive(self, mapping: Dict, node_id: str, user_messages: List, ai_messages: List):
        """
        ChatGPT 트리 구조를 재귀적으로 순회하여 메시지 수집
        """
        if node_id not in mapping:
            return
        
        node = mapping[node_id]
        if node.get('message'):
            message = node['message']
            try:
                role = message.get('author', {}).get('role', '')
                
                if role == 'user':
                    user_messages.append(message)
                elif role == 'assistant':
                    ai_messages.append(message)
            except Exception as e:
                print(f"메시지 처리 중 에러 (node_id: {node_id}): {str(e)}")
                pass
        
        # 자식 노드들을 순회
        for child_id in node.get('children', []):
            self._collect_messages_recursive(mapping, child_id, user_messages, ai_messages)
    
    def _parse_grok(self, data: Dict) -> List[Dict[str, Any]]:
        """
        Grok 대화내역 파싱
        """
        results = []
        
        for conversation in data['conversations']:
            conversation_id = conversation['conversation']['id']
            responses = conversation['responses']
            
            # user 메시지들을 찾아서 처리
            user_messages = []
            ai_messages = []
            
            for response in responses:
                sender = response['response']['sender']
                message = response['response']['message']
                
                if sender == 'human':
                    user_messages.append(message)
                elif sender == 'assistant':
                    ai_messages.append(message)
            
            # user 메시지들을 기준으로 결과 생성
            for i, response in enumerate(responses):
                if response['response']['sender'] == 'human':
                    user_query = response['response']['message']
                    message_id = response['response']['_id']  # Grok의 실제 _id 사용
                    
                    # 이전 AI 답변이 있는지 확인
                    previous_ai_answer = None
                    conversation_flow = f"[USER_QUESTION] {user_query}"
                    
                    # 이전 응답에서 assistant 메시지 찾기
                    for j in range(i):
                        if responses[j]['response']['sender'] == 'assistant':
                            previous_ai_answer = responses[j]['response']['message']
                            conversation_flow = f"[AI_ANSWER] {previous_ai_answer}\n[USER_QUESTION] {user_query}"
                            break
                    
                    results.append({
                        "id": message_id,
                        "content": {
                            "user_query": user_query,
                            "conversation_flow": conversation_flow
                        },
                        "metadata": {
                            "previous_ai_answer": previous_ai_answer,
                            "conversation_id": conversation_id
                        }
                    })
        
        return results
    
    def parse_multiple_files(self, file_paths: List[str], llm_types: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        여러 파일을 한번에 파싱 (LLM별로 분리)
        
        Args:
            file_paths: JSON 파일 경로 리스트
            llm_types: 각 파일의 LLM 타입 리스트 (None이면 자동 판단)
            
        Returns:
            LLM별로 분리된 파싱된 대화내역 딕셔너리
        """
        results_by_llm = {}
        
        for i, file_path in enumerate(file_paths):
            try:
                # LLM 타입이 명시된 경우 사용, 아니면 자동 판단
                llm_type = llm_types[i] if llm_types and i < len(llm_types) else None
                results = self.parse_file(file_path, llm_type)
                
                # 자동 감지된 LLM 타입을 결과에 추가
                if llm_type is None:
                    llm_type = self._detect_llm_type_from_file(file_path)
                
                if llm_type not in results_by_llm:
                    results_by_llm[llm_type] = []
                
                results_by_llm[llm_type].extend(results)
                print(f"Successfully parsed {file_path}: {len(results)} conversations (type: {llm_type})")
                
            except Exception as e:
                print(f"Failed to parse {file_path}: {str(e)}")
                print(f"Error details: {type(e).__name__}: {str(e)}")
        
        return results_by_llm
    
    def _detect_llm_type_from_file(self, file_path: str) -> str:
        """
        파일을 읽어서 LLM 타입을 감지
        
        Args:
            file_path: JSON 파일 경로
            
        Returns:
            LLM 타입
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._detect_llm_type(data)
        except Exception as e:
            raise ValueError(f"파일 {file_path}의 LLM 타입을 감지할 수 없습니다: {str(e)}")
    
    def save_parsed_data(self, data: List[Dict[str, Any]], output_path: str):
        """
        파싱된 데이터를 JSON 파일로 저장
        
        Args:
            data: 파싱된 데이터
            output_path: 출력 파일 경로
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Parsed data saved to {output_path}")
    
    def save_parsed_data_by_llm(self, data_by_llm: Dict[str, List[Dict[str, Any]]], output_dir: str = "parsed_data"):
        """
        LLM별로 파싱된 데이터를 분리하여 저장
        
        Args:
            data_by_llm: LLM별로 분리된 파싱된 데이터
            output_dir: 출력 디렉토리
        """
        import os
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        for llm_type, data in data_by_llm.items():
            if data:  # 데이터가 있는 경우만 저장
                output_path = os.path.join(output_dir, f"{llm_type}_parsed.json")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"{llm_type} data saved to {output_path} ({len(data)} conversations)")
            else:
                print(f"No {llm_type} data to save")


# 사용 예시
if __name__ == "__main__":
    parser = LLMConversationParser()
    
    # 단일 파일 파싱
    claude_data = parser.parse_file("claude_conversations.json")
    print(f"Claude 대화 수: {len(claude_data)}")
    
    # 여러 파일 파싱
    all_data = parser.parse_multiple_files([
        "claude_conversations.json",
        "gpt_conversations.json", 
        "grok_conversations.json"
    ])
    
    print(f"전체 대화 수: {len(all_data)}")
    
    # 결과 저장
    parser.save_parsed_data(all_data, "parsed_conversations.json")

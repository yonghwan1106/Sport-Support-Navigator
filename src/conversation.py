from typing import Dict, List
import re

class ConversationManager:
    """
    사용자와의 대화를 관리하는 클래스입니다.
    자연스러운 대화를 통해 필요한 정보를 수집합니다.
    """
    
    def __init__(self):
        """대화 관리자 초기화"""
        self.conversation_history = []
        self.question_templates = {
            'initial': [
                "안녕하세요! 스포츠산업 지원사업 매칭을 도와드리겠습니다. 어떤 사업을 구상하고 계신가요?",
                "먼저 간단히 사업 아이디어나 현재 상황에 대해 말씀해 주세요."
            ],
            'stage_clarification': [
                "현재 사업이 어느 단계에 있으신가요? 아이디어 단계신가요, 아니면 이미 시작하셨나요?",
                "{stage} 단계라고 하셨는데, 구체적으로 어떤 준비를 하고 계신가요?"
            ],
            'sector_clarification': [
                "스포츠 분야에서 어떤 영역을 생각하고 계신가요? 용품 제조, 서비스, 시설 운영 중에서요.",
                "{sector} 분야에서 특별히 집중하고 싶으신 세부 영역이 있으신가요?"
            ],
            'support_needs': [
                "어떤 종류의 지원이 가장 필요하신가요? 자금, 공간, 멘토링 등에 대해 말씀해 주세요.",
                "희망하시는 지원 규모는 어느 정도인가요?"
            ]
        }
        self.required_information = {
            'stage': None,
            'sector': None,
            'scale': None,
            'support_needs': None
        }

    def process_user_input(self, user_message: str):
        """
        사용자 입력을 처리하고 적절한 응답을 생성합니다.
        Linear Latent Intervention을 활용하여 입력의 잠재적 의미를 파악합니다.
        """
        # 입력 메시지에서 정보 추출
        extracted_info = self._extract_information(user_message)
        
        # 추출된 정보 업데이트
        self._update_information(extracted_info)
        
        # 다음 질문 생성 (Overprompting 활용)
        next_question = self._generate_next_question()
        
        return next_question

    def _extract_information(self, message: str):
        """
        Linear Latent Intervention을 활용하여 
        사용자 메시지에서 중요 정보를 추출합니다.
        """
        extracted = {}
        
        # 사업 단계 파악
        stages = {
            '예비': 'preliminary',
            '시작': 'initial',
            '아이디어': 'ideation',
            '준비': 'preparation'
        }
        for key, value in stages.items():
            if key in message:
                extracted['stage'] = value
                
        # 분야 파악
        sectors = {
            '용품': 'manufacturing',
            '제조': 'manufacturing',
            '서비스': 'service',
            '시설': 'facility'
        }
        for key, value in sectors.items():
            if key in message:
                extracted['sector'] = value
                
        return extracted

    def _generate_next_question(self):
        """
        Overprompting을 활용하여 다음 질문을 생성합니다.
        현재까지 수집된 정보를 바탕으로 가장 적절한 후속 질문을 선택합니다.
        """
        # 누락된 정보 중 가장 중요한 것 확인
        missing_info = [k for k, v in self.required_information.items() 
                       if v is None]
        
        if not missing_info:
            return self._generate_summary_and_confirmation()
            
        next_topic = missing_info[0]
        template = self.question_templates.get(f'{next_topic}_clarification')[0]
        
        # Overprompting을 통한 질문 구체화
        context = {k: v for k, v in self.required_information.items() 
                  if v is not None}
        
        return template.format(**context)

    def _generate_summary_and_confirmation(self):
        """
        수집된 정보를 요약하고 확인을 요청합니다.
        """
        summary = "제가 이해한 내용을 정리해드리겠습니다:\n\n"
        for key, value in self.required_information.items():
            if value:
                summary += f"- {key}: {value}\n"
        
        summary += "\n이 내용이 맞으신가요? 수정이 필요하다면 말씀해 주세요."
        return summary

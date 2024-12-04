from typing import Dict, List, Optional
import re
import random

class ConversationManager:
    """
    사용자와의 대화를 관리하는 클래스입니다.
    자연스러운 대화를 통해 필요한 정보를 수집하고, Linear Latent Intervention과
    Overprompting을 활용하여 더 정확한 정보를 추출합니다.
    """
    
    def __init__(self):
        """
        대화 관리자를 초기화합니다.
        대화 이력, 질문 템플릿, 필요한 정보 등의 상태를 설정합니다.
        """
        self.conversation_history = []
        self.question_templates = {
            'initial': [
                "안녕하세요! 스포츠산업 지원사업 매칭을 도와드리겠습니다. 어떤 사업을 구상하고 계신가요?",
                "먼저 간단히 사업 아이디어나 현재 상황에 대해 말씀해 주세요.",
                "스포츠산업 지원사업 매칭 시스템입니다. 어떤 계획을 가지고 계신지 편하게 말씀해 주세요."
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
        self.current_profile = {}

    def get_initial_message(self) -> str:
        """
        대화를 시작하는 첫 메시지를 생성합니다.
        
        Returns:
            str: 초기 대화 메시지
        """
        return random.choice(self.question_templates['initial'])

    def process_user_input(self, user_message: str) -> str:
        """
        사용자 입력을 처리하고 적절한 응답을 생성합니다.
        Linear Latent Intervention을 활용하여 입력의 잠재적 의미를 파악합니다.
        
        Args:
            user_message (str): 사용자 입력 메시지
            
        Returns:
            str: 시스템 응답 메시지
        """
        # 사용자 메시지 기록
        self.conversation_history.append({
            'role': 'user',
            'message': user_message
        })
        
        # 정보 추출 및 프로필 업데이트
        extracted_info = self._extract_information(user_message)
        self.current_profile.update(extracted_info)
        
        # 다음 질문 생성
        next_question = self._generate_next_question()
        
        # 시스템 응답 기록
        self.conversation_history.append({
            'role': 'system',
            'message': next_question
        })
        
        return next_question

    def get_current_profile(self) -> Dict:
        """
        현재까지 수집된 사용자 프로필을 반환합니다.
        
        Returns:
            Dict: 수집된 사용자 프로필 정보
        """
        return self.current_profile.copy()

    def is_profile_complete(self) -> bool:
        """
        필요한 모든 정보가 수집되었는지 확인합니다.
        
        Returns:
            bool: 프로필 완성 여부
        """
        return all(self.required_information.values())

    def _extract_information(self, message: str) -> Dict:
        """
        Linear Latent Intervention을 활용하여 사용자 메시지에서 중요 정보를 추출합니다.
        
        Args:
            message (str): 분석할 사용자 메시지
            
        Returns:
            Dict: 추출된 정보
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
                self.required_information['stage'] = value
                
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
                self.required_information['sector'] = value
                
        return extracted

    def _generate_next_question(self) -> str:
        """
        Overprompting을 활용하여 다음 질문을 생성합니다.
        
        Returns:
            str: 다음 질문
        """
        missing_info = [k for k, v in self.required_information.items() 
                       if v is None]
        
        if not missing_info:
            return self._generate_summary_and_confirmation()
            
        next_topic = missing_info[0]
        template = self.question_templates.get(f'{next_topic}_clarification', [''])[0]
        
        context = {k: v for k, v in self.required_information.items() 
                  if v is not None}
        
        try:
            return template.format(**context)
        except KeyError:
            return template

    def _generate_summary_and_confirmation(self) -> str:
        """
        수집된 정보를 요약하고 확인을 요청합니다.
        
        Returns:
            str: 요약 및 확인 메시지
        """
        summary = "제가 이해한 내용을 정리해드리겠습니다:\n\n"
        for key, value in self.required_information.items():
            if value:
                summary += f"- {key}: {value}\n"
        
        summary += "\n이 내용이 맞으신가요? 수정이 필요하다면 말씀해 주세요."
        return summary

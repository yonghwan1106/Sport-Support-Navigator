from typing import Dict, List, Optional
import re
from dataclasses import dataclass, field

@dataclass
class UserProfile:
    """사용자 프로필 정보를 저장하는 데이터 클래스"""
    stage: Optional[str] = None  # 사업 단계 (아이디어, 초기, 성장 등)
    sector: Optional[str] = None  # 사업 분야 (용품, 서비스, 시설)
    scale: Optional[str] = None  # 사업 규모
    support_needs: Optional[str] = None  # 필요한 지원 종류
    description: str = ""  # 사업 설명
    desired_support_scale: float = 0.0  # 희망 지원 규모

class ConversationManager:
    """
    사용자와의 대화를 관리하는 클래스입니다.
    자연스러운 대화를 통해 필요한 정보를 수집하고 적절한 지원사업을 매칭합니다.
    """
    
    def __init__(self):
        """대화 관리자 초기화"""
        self.conversation_history = []
        self.current_profile = UserProfile()
        self.state = 'initial'
        self.question_templates = {
            'initial': [
                "안녕하세요! 스포츠산업 지원사업 매칭을 도와드리겠습니다. 어떤 사업을 구상하고 계신가요?",
                "먼저 간단히 사업 아이디어나 현재 상황에 대해 말씀해 주세요.",
                "스포츠산업 지원사업 매칭 시스템입니다. 어떤 계획을 가지고 계신지 편하게 말씀해 주세요."
            ],
            'stage': [
                "현재 사업이 어느 단계에 있으신가요? (예: 아이디어 단계, 초기 창업, 성장 단계)",
                "{stage} 단계라고 하셨는데, 구체적으로 어떤 준비를 하고 계신가요?"
            ],
            'sector': [
                "스포츠 분야에서 어떤 영역을 생각하고 계신가요? (예: 용품 제조, 서비스, 시설 운영)",
                "{sector} 분야에서 특별히 집중하고 싶으신 세부 영역이 있으신가요?"
            ],
            'scale': [
                "예상하시는 사업 규모는 어느 정도인가요? (예: 소규모, 중규모, 대규모)",
                "희망하시는 지원 규모는 어느 정도인가요?"
            ],
            'support_needs': [
                "어떤 종류의 지원이 가장 필요하신가요? (예: 자금, 공간, 멘토링 등)"
            ]
        }

    def process_user_input(self, user_message: str) -> str:
        """
        사용자 입력을 처리하고 적절한 응답을 생성합니다.
        
        Args:
            user_message: 사용자가 입력한 메시지
            
        Returns:
            다음 질문 또는 응답 메시지
        """
        # 사용자 메시지 저장
        self.conversation_history.append({
            'role': 'user',
            'message': user_message
        })

        # 메시지에서 정보 추출 및 상태 업데이트
        extracted_info = self._extract_information(user_message)
        self._update_profile(extracted_info)
        
        # 다음 응답 생성
        response = self._generate_next_response()
        
        # 시스템 응답 저장
        self.conversation_history.append({
            'role': 'system',
            'message': response
        })
        
        return response

    def _extract_information(self, message: str) -> Dict:
        """
        사용자 메시지에서 중요 정보를 추출합니다.
        
        Args:
            message: 분석할 사용자 메시지
            
        Returns:
            추출된 정보를 담은 딕셔너리
        """
        info = {}
        
        # 사업 단계 파악
        stage_keywords = {
            'ideation': ['아이디어', '구상', '계획'],
            'initial': ['초기', '시작', '준비'],
            'growth': ['성장', '확장', '도약'],
            'stable': ['안정', '성숙']
        }
        
        for stage, keywords in stage_keywords.items():
            if any(keyword in message for keyword in keywords):
                info['stage'] = stage
                
        # 사업 분야 파악
        sector_keywords = {
            'manufacturing': ['제조', '용품', '장비'],
            'service': ['서비스', '교육', '컨설팅'],
            'facility': ['시설', '공간', '센터']
        }
        
        for sector, keywords in sector_keywords.items():
            if any(keyword in message for keyword in keywords):
                info['sector'] = sector
                
        return info

    def _update_profile(self, new_info: Dict):
        """
        추출된 정보로 사용자 프로필을 업데이트합니다.
        
        Args:
            new_info: 새로 추출된 정보
        """
        for key, value in new_info.items():
            setattr(self.current_profile, key, value)
            
        # 상태 업데이트
        if new_info.get('stage') and self.state == 'initial':
            self.state = 'ask_sector'
        elif new_info.get('sector') and self.state == 'ask_sector':
            self.state = 'ask_scale'
        elif self.state == 'ask_scale' and 'scale' in new_info:
            self.state = 'ask_support'

    def _generate_next_response(self) -> str:
        """
        현재 상태에 따라 다음 응답을 생성합니다.
        
        Returns:
            다음 질문 또는 응답 메시지
        """
        if self.state == 'initial':
            return self.question_templates['stage'][0]
        elif self.state == 'ask_sector':
            return self.question_templates['sector'][0]
        elif self.state == 'ask_scale':
            return self.question_templates['scale'][0]
        elif self.state == 'ask_support':
            return self.question_templates['support_needs'][0]
        else:
            return self._generate_summary()

    def _generate_summary(self) -> str:
        """
        수집된 정보를 요약하여 제시합니다.
        
        Returns:
            요약 메시지
        """
        summary = "지금까지 말씀해 주신 내용을 정리해보겠습니다:\n\n"
        
        if self.current_profile.stage:
            summary += f"- 사업 단계: {self.current_profile.stage}\n"
        if self.current_profile.sector:
            summary += f"- 사업 분야: {self.current_profile.sector}\n"
        if self.current_profile.scale:
            summary += f"- 사업 규모: {self.current_profile.scale}\n"
        if self.current_profile.support_needs:
            summary += f"- 필요한 지원: {self.current_profile.support_needs}\n"
            
        summary += "\n이 내용이 맞으시다면, 적합한 지원사업을 찾아드리겠습니다."
        return summary

    def get_current_profile(self) -> UserProfile:
        """현재 사용자 프로필을 반환합니다."""
        return self.current_profile

    def is_profile_complete(self) -> bool:
        """프로필 정보가 충분히 수집되었는지 확인합니다."""
        return all([
            self.current_profile.stage,
            self.current_profile.sector,
            self.current_profile.support_needs
        ])

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum, auto
import random

class ConversationState(Enum):
    """대화 상태를 관리하는 열거형 클래스"""
    GREETING = auto()          # 초기 인사
    ASKING_STAGE = auto()      # 사업 단계 질문
    ASKING_SECTOR = auto()     # 사업 분야 질문
    ASKING_SCALE = auto()      # 사업 규모 질문
    ASKING_SUPPORT = auto()    # 지원 종류 질문
    CONFIRMING = auto()        # 정보 확인
    COMPLETED = auto()         # 대화 완료

@dataclass
class UserProfile:
    """사용자 프로필 정보를 저장하는 데이터 클래스"""
    stage: Optional[str] = None         # 사업 단계
    sector: Optional[str] = None        # 사업 분야
    scale: Optional[str] = None         # 사업 규모
    support_needs: Optional[str] = None # 필요한 지원
    description: str = ""               # 상세 설명

class ConversationManager:
    """대화 관리 및 사용자 정보 수집을 담당하는 클래스"""
    
    def __init__(self):
        """대화 관리자 초기화"""
        self.profile = UserProfile()
        self.state = ConversationState.GREETING
        self.conversation_history: List[Dict[str, str]] = []
        
        # 단계별 키워드 정의
        self.stage_keywords = {
            'ideation': ['아이디어', '구상', '계획', '준비'],
            'initial': ['초기', '시작', '창업', '1년차'],
            'growth': ['성장', '도약', '확장', '발전'],
            'stable': ['안정', '성숙', '정착']
        }
        
        self.sector_keywords = {
            'manufacturing': ['제조', '용품', '장비', '제작'],
            'service': ['서비스', '교육', '컨설팅'],
            'facility': ['시설', '공간', '센터', '체육관']
        }
        
        # 사용자 친화적 표시를 위한 매핑
        self.display_names = {
            'stage': {
                'ideation': '아이디어 단계',
                'initial': '초기 창업 단계',
                'growth': '성장 단계',
                'stable': '안정화 단계'
            },
            'sector': {
                'manufacturing': '용품 제조',
                'service': '서비스',
                'facility': '시설 운영'
            }
        }

        # 대화 템플릿 정의
        self.templates = {
            ConversationState.GREETING: [
                "안녕하세요! 스포츠산업 지원사업 매칭을 도와드리겠습니다. 어떤 계획을 가지고 계신가요?",
                "스포츠산업 지원사업 매칭 시스템입니다. 어떤 계획을 가지고 계신지 편하게 말씀해 주세요."
            ],
            ConversationState.ASKING_STAGE: [
                "현재 사업이 어느 단계에 있으신가요? (예: 아이디어 단계, 초기 창업, 성장 단계)",
                "사업 진행 단계가 어떻게 되시나요? 아이디어 구상 중이신가요, 아니면 이미 시작하셨나요?"
            ],
            ConversationState.ASKING_SECTOR: [
                "스포츠 분야에서 어떤 영역을 생각하고 계신가요? (용품 제조, 서비스, 시설 운영)",
                "계획하시는 사업의 분야가 어떻게 되시나요? 용품을 만드시나요, 서비스를 제공하시나요?"
            ],
            ConversationState.ASKING_SCALE: [
                "예상하시는 사업 규모는 어느 정도인가요? (소규모, 중규모, 대규모)",
                "계획하시는 사업의 규모가 어느 정도인가요?"
            ],
            ConversationState.ASKING_SUPPORT: [
                "어떤 종류의 지원이 가장 필요하신가요? (자금, 공간, 멘토링, 교육 등)",
                "어떤 부분에서 도움이 필요하신가요?"
            ]
        }

    def get_initial_message(self) -> str:
        """초기 환영 메시지 반환"""
        return random.choice(self.templates[ConversationState.GREETING])

    def process_user_input(self, user_message: str) -> str:
        """사용자 입력 처리 및 다음 응답 생성"""
        # 사용자 메시지 저장
        self.conversation_history.append({
            'role': 'user',
            'message': user_message
        })

        # 현재 상태에 따른 정보 추출 및 처리
        if self.state == ConversationState.GREETING:
            self.state = ConversationState.ASKING_STAGE
            response = random.choice(self.templates[ConversationState.ASKING_STAGE])
        
        elif self.state == ConversationState.ASKING_STAGE:
            stage = self._extract_stage(user_message)
            if stage:
                self.profile.stage = stage
                self.state = ConversationState.ASKING_SECTOR
                response = random.choice(self.templates[ConversationState.ASKING_SECTOR])
            else:
                response = "죄송합니다. 사업 단계를 명확히 알려주시겠어요? (아이디어/초기/성장/안정)"
        
        elif self.state == ConversationState.ASKING_SECTOR:
            sector = self._extract_sector(user_message)
            if sector:
                self.profile.sector = sector
                self.state = ConversationState.ASKING_SCALE
                response = random.choice(self.templates[ConversationState.ASKING_SCALE])
            else:
                response = "죄송합니다. 사업 분야를 명확히 말씀해 주시겠어요? (용품 제조/서비스/시설)"
        
        elif self.state == ConversationState.ASKING_SCALE:
            self.profile.scale = user_message  # 규모는 자유 형식으로 저장
            self.state = ConversationState.ASKING_SUPPORT
            response = random.choice(self.templates[ConversationState.ASKING_SUPPORT])
        
        elif self.state == ConversationState.ASKING_SUPPORT:
            self.profile.support_needs = user_message
            self.state = ConversationState.COMPLETED
            response = self._generate_summary()
        
        else:
            response = "죄송합니다. 대화가 초기화되었습니다. 다시 시작해 주시겠어요?"
            self.state = ConversationState.GREETING

        # 시스템 응답 저장
        self.conversation_history.append({
            'role': 'system',
            'message': response
        })

        return response

    def _extract_stage(self, message: str) -> Optional[str]:
        """사업 단계 정보 추출"""
        for stage, keywords in self.stage_keywords.items():
            if any(keyword in message for keyword in keywords):
                return stage
        return None

    def _extract_sector(self, message: str) -> Optional[str]:
        """사업 분야 정보 추출"""
        for sector, keywords in self.sector_keywords.items():
            if any(keyword in message for keyword in keywords):
                return sector
        return None

    def _generate_summary(self) -> str:
        """수집된 정보 요약"""
        summary = "지금까지 말씀해 주신 내용을 정리해보겠습니다:\n\n"
        
        if self.profile.stage:
            stage_name = self.display_names['stage'].get(self.profile.stage, self.profile.stage)
            summary += f"- 사업 단계: {stage_name}\n"
            
        if self.profile.sector:
            sector_name = self.display_names['sector'].get(self.profile.sector, self.profile.sector)
            summary += f"- 사업 분야: {sector_name}\n"
            
        if self.profile.scale:
            summary += f"- 사업 규모: {self.profile.scale}\n"
            
        if self.profile.support_needs:
            summary += f"- 필요한 지원: {self.profile.support_needs}\n"
            
        summary += "\n이 정보를 바탕으로 적합한 지원사업을 찾아드리겠습니다."
        return summary

    def get_current_profile(self) -> UserProfile:
        """현재 프로필 반환"""
        return self.profile

    def is_profile_complete(self) -> bool:
        """프로필 완성 여부 확인"""
        return self.state == ConversationState.COMPLETED

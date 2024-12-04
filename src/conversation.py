# src/conversation.py

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import random
import re
import logging

class ConversationState(Enum):
    """대화 상태를 관리하는 열거형 클래스"""
    INITIAL = "initial"           # 초기 상태
    COLLECTING_STAGE = "stage"    # 사업 단계 수집
    COLLECTING_SECTOR = "sector"  # 사업 분야 수집
    COLLECTING_SCALE = "scale"    # 규모 수집
    COLLECTING_NEEDS = "needs"    # 지원 needs 수집
    CONFIRMING = "confirming"     # 정보 확인
    COMPLETED = "completed"       # 완료

@dataclass
class UserProfile:
    """사용자 프로필 정보를 저장하는 데이터 클래스"""
    stage: Optional[str] = None         # 사업 단계
    sector: Optional[str] = None        # 사업 분야
    scale: Optional[str] = None         # 규모
    support_needs: Optional[str] = None # 지원 종류
    description: str = ""               # 사업 설명
    
    def is_complete(self) -> bool:
        """프로필 정보가 충분한지 확인"""
        return bool(self.stage and self.sector and self.support_needs)
    
    def to_dict(self) -> Dict:
        """프로필을 딕셔너리로 변환"""
        return {
            'stage': self.stage,
            'sector': self.sector,
            'scale': self.scale,
            'support_needs': self.support_needs,
            'description': self.description
        }

class ConversationManager:
    """대화 관리 및 정보 수집을 담당하는 클래스"""

    def get_current_profile(self) -> UserProfile:
    """
    현재 사용자의 프로필 정보를 반환합니다.
    이 메서드는 대화 과정에서 수집된 모든 사용자 정보를 포함하는
    UserProfile 객체를 반환합니다.
    
    Returns:
        UserProfile: 현재까지 수집된 사용자 프로필 정보를 담고 있는 객체
            - stage: 사업 단계 (예: 아이디어, 초기, 성장)
            - sector: 사업 분야 (예: 제조, 서비스, 시설)
            - scale: 사업 규모
            - support_needs: 필요한 지원 종류
            - description: 사업 설명
    """
    return self.profile

    def is_profile_complete(self) -> bool:
        """
        현재 프로필 정보가 충분히 수집되었는지 확인합니다.
        사업 단계, 분야, 지원 종류와 같은 필수 정보가 모두 있는지 검사합니다.
        
        Returns:
            bool: 필수 정보가 모두 수집되었는지 여부
        """
        return self.profile.is_complete()
    
    def __init__(self):
        """대화 관리자를 초기화합니다."""
        self.profile = UserProfile()
        self.state = ConversationState.INITIAL
        self.conversation_history = []
        self.last_question = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self._initialize_templates()
        self._initialize_keywords()
    
    def get_initial_message(self) -> str:
        """대화 시작시 보여줄 초기 메시지를 반환합니다."""
        initial_message = random.choice(self.templates["initial"])
        self._add_to_history("system", initial_message)
        return initial_message

    def _initialize_templates(self):
        """응답 템플릿을 초기화합니다."""
        self.templates = {
            "initial": [
                "안녕하세요! 스포츠산업 지원사업 매칭을 도와드리겠습니다. 어떤 사업을 구상하고 계신가요?",
                "스포츠산업 지원사업 매칭 시스템입니다. 어떤 계획을 가지고 계신지 편하게 말씀해 주세요.",
            ],
            "stage_question": [
                "현재 사업이 어느 단계에 있으신가요? (예: 아이디어 단계, 초기 창업, 성장 단계)",
                "구체적으로 어느 단계까지 진행되었나요? (아이디어/초기/성장)",
            ],
            "sector_question": [
                "스포츠 분야에서 어떤 영역을 생각하고 계신가요? (예: 용품 제조, 서비스, 시설 운영)",
                "구체적으로 어떤 스포츠 분야를 고려하고 계신가요?",
            ],
            "scale_question": [
                "예상하시는 사업 규모는 어느 정도인가요? (예: 소규모, 중규모, 대규모)",
                "사업 규모를 어느 정도로 계획하고 계신가요?",
            ],
            "needs_question": [
                "어떤 종류의 지원이 가장 필요하신가요? (예: 자금, 공간, 멘토링 등)",
                "현재 가장 필요하신 지원은 무엇인가요?",
            ],
            "confirm": "지금까지 말씀해 주신 내용을 정리해보겠습니다:",
            "error": "죄송합니다. 다시 한 번 말씀해 주시겠어요?"
        }

    def _initialize_keywords(self):
        """키워드 매칭을 위한 사전을 초기화합니다."""
        self.keywords = {
            "stage": {
                "ideation": ["아이디어", "구상", "계획", "준비"],
                "initial": ["초기", "시작", "창업"],
                "growth": ["성장", "확장", "도약"],
                "stable": ["안정", "성숙", "정착"]
            },
            "sector": {
                "manufacturing": ["제조", "용품", "장비"],
                "service": ["서비스", "교육", "컨설팅"],
                "facility": ["시설", "공간", "센터"]
            },
            "scale": {
                "small": ["소규모", "작은", "1인"],
                "medium": ["중규모", "중간"],
                "large": ["대규모", "큰"]
            },
            "needs": {
                "funding": ["자금", "투자", "금융"],
                "space": ["공간", "시설", "장소"],
                "mentoring": ["멘토링", "교육", "컨설팅"],
                "marketing": ["마케팅", "홍보", "영업"]
            }
        }

    def process_user_input(self, user_message: str) -> str:
        """사용자 입력을 처리하고 적절한 응답을 생성합니다."""
        try:
            self._add_to_history("user", user_message)
            
            if self._is_duplicate_message(user_message):
                return self._get_alternative_question()
                
            self._process_message(user_message)
            
            response = self._generate_response()
            self._add_to_history("system", response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing user input: {e}")
            return self.templates["error"]

    def _process_message(self, message: str):
        """메시지를 처리하고 상태를 업데이트합니다."""
        if self.state == ConversationState.INITIAL:
            extracted_info = self._extract_initial_info(message)
            if extracted_info:
                self._update_profile(extracted_info)
            self.state = ConversationState.COLLECTING_STAGE
            
        elif self.state == ConversationState.COLLECTING_STAGE:
            stage = self._extract_stage(message)
            if stage:
                self.profile.stage = stage
                self.state = ConversationState.COLLECTING_SECTOR
                
        elif self.state == ConversationState.COLLECTING_SECTOR:
            sector = self._extract_sector(message)
            if sector:
                self.profile.sector = sector
                self.state = ConversationState.COLLECTING_SCALE
                
        elif self.state == ConversationState.COLLECTING_SCALE:
            scale = self._extract_scale(message)
            if scale:
                self.profile.scale = scale
                self.state = ConversationState.COLLECTING_NEEDS
                
        elif self.state == ConversationState.COLLECTING_NEEDS:
            needs = self._extract_needs(message)
            if needs:
                self.profile.support_needs = needs
                self.state = ConversationState.CONFIRMING

    def _extract_initial_info(self, message: str) -> Dict:
        """초기 메시지에서 관련 정보를 추출합니다."""
        info = {}
        for category, keyword_dict in self.keywords.items():
            for key, keywords in keyword_dict.items():
                if any(keyword in message for keyword in keywords):
                    info[category] = key
                    break
        return info

    def _extract_stage(self, message: str) -> Optional[str]:
        """사업 단계 정보를 추출합니다."""
        for stage, keywords in self.keywords["stage"].items():
            if any(keyword in message for keyword in keywords):
                return stage
        return None

    def _extract_sector(self, message: str) -> Optional[str]:
        """사업 분야 정보를 추출합니다."""
        for sector, keywords in self.keywords["sector"].items():
            if any(keyword in message for keyword in keywords):
                return sector
        return None

    def _extract_scale(self, message: str) -> Optional[str]:
        """사업 규모 정보를 추출합니다."""
        for scale, keywords in self.keywords["scale"].items():
            if any(keyword in message for keyword in keywords):
                return scale
        return None

    def _extract_needs(self, message: str) -> Optional[str]:
        """지원 needs 정보를 추출합니다."""
        for need, keywords in self.keywords["needs"].items():
            if any(keyword in message for keyword in keywords):
                return need
        return None

    def _generate_response(self) -> str:
        """현재 상태에 맞는 응답을 생성합니다."""
        if self.state == ConversationState.INITIAL:
            return random.choice(self.templates["initial"])
            
        elif self.state == ConversationState.COLLECTING_STAGE:
            return random.choice(self.templates["stage_question"])
            
        elif self.state == ConversationState.COLLECTING_SECTOR:
            return random.choice(self.templates["sector_question"])
            
        elif self.state == ConversationState.COLLECTING_SCALE:
            return random.choice(self.templates["scale_question"])
            
        elif self.state == ConversationState.COLLECTING_NEEDS:
            return random.choice(self.templates["needs_question"])
            
        elif self.state == ConversationState.CONFIRMING:
            return self._generate_summary()
            
        else:
            return self.templates["error"]

    def _generate_summary(self) -> str:
        """수집된 정보를 요약하여 보여줍니다."""
        summary = self.templates["confirm"] + "\n\n"
        
        if self.profile.stage:
            summary += f"- 사업 단계: {self._get_korean_term('stage', self.profile.stage)}\n"
        if self.profile.sector:
            summary += f"- 사업 분야: {self._get_korean_term('sector', self.profile.sector)}\n"
        if self.profile.scale:
            summary += f"- 사업 규모: {self._get_korean_term('scale', self.profile.scale)}\n"
        if self.profile.support_needs:
            summary += f"- 필요한 지원: {self._get_korean_term('needs', self.profile.support_needs)}\n"
            
        summary += "\n이 내용이 맞으시다면, 적합한 지원사업을 찾아드리겠습니다."
        return summary

    def _get_korean_term(self, category: str, key: str) -> str:
        """영문 키워드에 대응하는 한글 용어를 반환합니다."""
        korean_terms = {
            "stage": {
                "ideation": "아이디어 단계",
                "initial": "초기 창업",
                "growth": "성장 단계",
                "stable": "안정화 단계"
            },
            "sector": {
                "manufacturing": "용품 제조",
                "service": "서비스",
                "facility": "시설 운영"
            },
            "scale": {
                "small": "소규모",
                "medium": "중규모",
                "large": "대규모"
            },
            "needs": {
                "funding": "자금 지원",
                "space": "공간 지원",
                "mentoring": "멘토링",
                "marketing": "마케팅 지원"
            }
        }
        return korean_terms.get(category, {}).get(key, key)

    def _add_to_history(self, role: str, message: str):
        """대화 이력에 새로운 메시지를 추가합니다."""
        self.conversation_history.append({
            "role": role,
            "message": message,
            "state": self.state.value
        })

    def _is_duplicate_message(self, message: str) -> bool:
        """메시지가 이전 대화에서 중복되는지 확인합니다."""
        if len(self.conversation_history) >= 2:
            recent_messages = [
                msg["message"] for msg in self.conversation_history[-2:]
                if msg["role"] == "user"
            ]
            return message in recent_messages
        return False

    def _get_alternative_question(self) -> str:
        """현재 상태에 맞는 대체 질문을 생성합니다."""
        if self.state == ConversationState.COLLECTING_STAGE:
            return self.templates["stage_question"][1]
        elif self.state == ConversationState.COLLECTING_SECTOR:
            return self.templates["sector_question"][1]
        elif self.state == ConversationState.COLLECTING_SCALE:
            return self.templates["scale_question"][1]
        elif self.state == ConversationState.COLLECTING_NEEDS:
            return self.templates["needs_question"][1]
        else:
            return self.templates["error"]

    def reset_conversation(self):
        """대화 상태를 초기화합니다."""
        self.profile = UserProfile()
        self.state = ConversationState.INITIAL
        self.conversation_history = []
        self.last_question = None
        self.logger.info("Conversation reset completed")

    def get_conversation_summary(self) -> Dict:
        """
        현재까지의 대화 내용과 수집된 정보를 요약하여 반환합니다.
        
        Returns:
            Dict: 대화 상태를 나타내는 딕셔너리로 다음 정보를 포함합니다:
                - profile: 수집된 사용자 프로필 정보
                - state: 현재 대화 상태
                - conversation_length: 총 대화 길이
                - is_complete: 프로필 정보 수집 완료 여부
        """
        return {
            'profile': self.profile.to_dict(),
            'state': self.state.value,
            'conversation_length': len(self.conversation_history),
            'is_complete': self.profile.is_complete()
        }

    def get_last_state(self) -> str:
        """
        가장 최근의 대화 상태를 반환합니다.
        이 정보는 대화 흐름 제어와 사용자 인터페이스 업데이트에 사용됩니다.
        
        Returns:
            str: 현재 대화 상태 값 (initial, stage, sector 등)
        """
        return self.state.value

    def validate_profile(self) -> List[str]:
        """
        현재 프로필 정보의 유효성을 검사하고 누락된 정보를 확인합니다.
        필수 필드의 존재 여부를 검사하여 미수집된 정보가 있는지 확인합니다.
        
        Returns:
            List[str]: 누락된 정보 필드명 목록
        """
        missing_fields = []
        profile_dict = self.profile.to_dict()
        
        required_fields = {
            'stage': '사업 단계',
            'sector': '사업 분야',
            'support_needs': '필요한 지원'
        }
        
        for field, display_name in required_fields.items():
            if not profile_dict.get(field):
                missing_fields.append(display_name)
                
        return missing_fields

    def handle_error(self, error_type: str) -> str:
        """
        대화 중 발생하는 다양한 오류 상황을 처리합니다.
        각 오류 유형에 맞는 친절한 안내 메시지를 생성하여 반환합니다.
        
        Args:
            error_type (str): 오류 유형
                - 'duplicate': 중복 답변
                - 'invalid': 잘못된 입력
                - 'missing': 누락된 정보
                - 'system': 시스템 오류
                
        Returns:
            str: 오류 상황에 대한 안내 메시지
        """
        error_responses = {
            'duplicate': "앞서 주신 답변과 동일합니다. 조금 더 구체적으로 말씀해 주시겠어요?",
            'invalid': "죄송합니다. 잘 이해하지 못했습니다. 다시 한 번 설명해 주시겠어요?",
            'missing': "몇 가지 정보가 더 필요합니다. 차근차근 여쭤보도록 하겠습니다.",
            'system': "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해 주시겠어요?"
        }
        
        response = error_responses.get(error_type, self.templates["error"])
        self.logger.warning(f"Error handled: {error_type}")
        return response

    def __str__(self) -> str:
        """
        현재 대화 관리자의 상태를 문자열로 표현합니다.
        디버깅과 로깅 목적으로 주요 상태 정보를 포함합니다.
        
        Returns:
            str: 현재 상태 정보를 담은 문자열
        """
        return (f"ConversationManager(state={self.state.value}, "
                f"profile_complete={self.profile.is_complete()}, "
                f"history_length={len(self.conversation_history)})")

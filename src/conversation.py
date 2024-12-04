from typing import Dict, List, Optional
import random
import re
from dataclasses import dataclass, field

@dataclass
class UserProfile:
   """
   사용자 프로필 정보를 저장하는 데이터 클래스입니다.
   각 필드는 대화를 통해 수집되는 중요 정보를 담고 있습니다.
   """
   stage: Optional[str] = None         # 사업 단계 (아이디어, 초기, 성장 등)
   sector: Optional[str] = None        # 사업 분야 (용품, 서비스, 시설)
   scale: Optional[str] = None         # 사업 규모 
   support_needs: Optional[str] = None # 필요한 지원 종류
   description: str = ""               # 사업 설명
   desired_support_scale: float = 0.0  # 희망 지원 규모

class ConversationManager:
   """
   사용자와의 대화를 관리하는 클래스입니다.
   자연스러운 대화 흐름을 통해 필요한 정보를 수집하고 
   적절한 지원사업을 매칭하는 역할을 담당합니다.
   """
   
   def __init__(self):
       """
       대화 관리자를 초기화합니다.
       대화 이력, 사용자 프로필, 상태 관리 등의 기본 설정을 수행합니다.
       """
       self.conversation_history = []
       self.current_profile = UserProfile()
       self.state = 'initial'
       
       # 다양한 상황에 맞는 질문 템플릿 정의
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

   def get_initial_message(self) -> str:
       """
       대화 시작시 보여줄 초기 메시지를 반환합니다.
       
       Returns:
           str: 환영 메시지
       """
       return random.choice(self.question_templates['initial'])

   def process_user_input(self, user_message: str) -> str:
       """
       사용자 입력을 처리하고 적절한 응답을 생성합니다.
       
       Args:
           user_message (str): 사용자가 입력한 메시지
           
       Returns:
           str: 시스템의 다음 응답
       """
       # 사용자 입력 처리 및 대화 이력 저장
       self._add_to_history('user', user_message)
       
       # 이전 답변 확인하여 중복 방지
       if not self._is_duplicate_answer(user_message):
           # 정보 추출 및 프로필 업데이트
           extracted_info = self._extract_information(user_message)
           self._update_profile(extracted_info)
           
           # 다음 응답 생성
           response = self._generate_next_response()
           self._add_to_history('system', response)
           
           return response
       else:
           # 중복 답변인 경우 다른 표현으로 재질문
           return self._rephrase_question()

   def _add_to_history(self, role: str, message: str):
       """
       대화 이력에 새로운 메시지를 추가합니다.
       
       Args:
           role (str): 메시지 발신자 ('user' 또는 'system')
           message (str): 저장할 메시지
       """
       self.conversation_history.append({
           'role': role,
           'message': message
       })

   def _is_duplicate_answer(self, message: str) -> bool:
       """
       현재 메시지가 이전 답변과 중복되는지 확인합니다.
       
       Args:
           message (str): 확인할 메시지
           
       Returns:
           bool: 중복 여부
       """
       if len(self.conversation_history) < 2:
           return False
           
       recent_messages = [msg['message'] for msg in self.conversation_history[-2:]]
       return message in recent_messages

   def _extract_information(self, message: str) -> Dict:
       """
       사용자 메시지에서 중요 정보를 추출합니다.
       
       Args:
           message (str): 분석할 사용자 메시지
           
       Returns:
           Dict: 추출된 정보를 담은 딕셔너리
       """
       info = {}
       
       # 사업 단계 파악
       stage_keywords = {
           'ideation': ['아이디어', '구상', '계획', '준비단계'],
           'initial': ['초기', '시작', '1년차'],
           'growth': ['성장', '도약', '확장'],
           'stable': ['안정', '성숙', '정착']
       }
       
       # 사업 분야 파악
       sector_keywords = {
           'manufacturing': ['제조', '용품', '장비', '제작'],
           'service': ['서비스', '교육', '컨설팅'],
           'facility': ['시설', '공간', '센터', '체육관']
       }
       
       # 키워드 매칭으로 정보 추출
       for stage, keywords in stage_keywords.items():
           if any(keyword in message for keyword in keywords):
               info['stage'] = stage
               break
               
       for sector, keywords in sector_keywords.items():
           if any(keyword in message for keyword in keywords):
               info['sector'] = sector
               break
               
       return info

   def _update_profile(self, new_info: Dict):
       """
       추출된 정보로 사용자 프로필을 업데이트하고 대화 상태를 전이합니다.
       
       Args:
           new_info (Dict): 새로 추출된 정보
       """
       # 프로필 정보 업데이트
       for key, value in new_info.items():
           if value:  # 값이 있는 경우에만 업데이트
               setattr(self.current_profile, key, value)
       
       # 상태 전이 로직
       if new_info.get('stage') and self.state == 'initial':
           self.state = 'ask_sector'
       elif new_info.get('sector') and self.state == 'ask_sector':
           self.state = 'ask_scale'
       elif new_info.get('scale') and self.state == 'ask_scale':
           self.state = 'ask_support'

   def _generate_next_response(self) -> str:
       """
       현재 상태와 수집된 정보를 바탕으로 다음 응답을 생성합니다.
       
       Returns:
           str: 다음 질문 또는 응답 메시지
       """
       if self.is_profile_complete():
           return self._generate_summary()
           
       if self.state == 'initial':
           return self.question_templates['stage'][0]
       elif self.state == 'ask_sector':
           return self.question_templates['sector'][0]
       elif self.state == 'ask_scale':
           return self.question_templates['scale'][0]
       elif self.state == 'ask_support':
           return self.question_templates['support_needs'][0]
       
       return self.question_templates['initial'][0]

   def _rephrase_question(self) -> str:
       """
       현재 질문을 다른 표현으로 바꾸어 제시합니다.
       
       Returns:
           str: 바꾸어 표현된 질문
       """
       current_state_questions = self.question_templates.get(self.state, [])
       if len(current_state_questions) > 1:
           return random.choice(current_state_questions[1:])
       return current_state_questions[0] if current_state_questions else "죄송합니다. 다시 한 번 말씀해 주시겠어요?"

   def _generate_summary(self) -> str:
       """
       수집된 정보를 요약하여 제시합니다.
       
       Returns:
           str: 요약 메시지
       """
       summary = "지금까지 말씀해 주신 내용을 정리해보겠습니다:\n\n"
       
       stage_names = {
           'ideation': '아이디어 단계',
           'initial': '초기 단계',
           'growth': '성장 단계',
           'stable': '안정화 단계'
       }
       
       sector_names = {
           'manufacturing': '용품 제조',
           'service': '서비스',
           'facility': '시설 운영'
       }
       
       if self.current_profile.stage:
           summary += f"- 사업 단계: {stage_names.get(self.current_profile.stage, self.current_profile.stage)}\n"
       if self.current_profile.sector:
           summary += f"- 사업 분야: {sector_names.get(self.current_profile.sector, self.current_profile.sector)}\n"
       if self.current_profile.scale:
           summary += f"- 사업 규모: {self.current_profile.scale}\n"
       if self.current_profile.support_needs:
           summary += f"- 필요한 지원: {self.current_profile.support_needs}\n"
           
       summary += "\n이 내용이 맞으시다면, 적합한 지원사업을 찾아드리겠습니다."
       return summary

   def get_current_profile(self) -> UserProfile:
       """
       현재 사용자 프로필을 반환합니다.
       
       Returns:
           UserProfile: 현재까지 수집된 사용자 프로필 정보
       """
       return self.current_profile

   def is_profile_complete(self) -> bool:
       """
       프로필 정보가 충분히 수집되었는지 확인합니다.
       
       Returns:
           bool: 프로필 완성 여부
       """
       required_fields = ['stage', 'sector', 'support_needs']
       return all(getattr(self.current_profile, field) for field in required_fields)

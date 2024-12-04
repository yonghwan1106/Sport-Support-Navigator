import streamlit as st
from src.data_processor import DataProcessor
from src.matcher import ProgramMatcher
from src.conversation import ConversationManager

class SportSupportNavigator:
    def __init__(self):
        """
        SportSupportNavigator 초기화
        데이터 처리기, 매칭 엔진, 대화 관리자를 설정하고 세션 상태를 초기화합니다.
        """
        # 기본 컴포넌트 초기화
        self.data_processor = DataProcessor()
        self.processed_data = self.data_processor.preprocess_support_programs()
        self.matcher = ProgramMatcher(self.processed_data)
        self.conversation_manager = ConversationManager()
        
        # 세션 상태 초기화
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {}
        if 'ready_for_matching' not in st.session_state:
            st.session_state.ready_for_matching = False
            
    def run(self):
        """
        메인 애플리케이션 실행
        대화형 인터페이스를 통해 사용자와 상호작용하고 매칭 결과를 보여줍니다.
        """
        st.title("Sport Support Navigator")
        st.subheader("스포츠산업 지원사업 지능형 매칭 시스템")
        
        # 대화 히스토리 표시
        self._display_conversation_history()
        
        # 사용자 입력 처리
        self._handle_user_input()
        
        # 매칭 결과 표시 (준비되었을 때)
        if st.session_state.ready_for_matching:
            self._show_matching_results()
            
    def _display_conversation_history(self):
        """
        대화 히스토리를 시각적으로 표시합니다.
        시스템 메시지와 사용자 메시지를 구분하여 보여줍니다.
        """
        for message in st.session_state.conversation_history:
            if message['type'] == 'system':
                st.write(f"🤖 {message['text']}")
            else:
                st.write(f"👤 {message['text']}")
                
        # 첫 대화 시작
        if not st.session_state.conversation_history:
            initial_message = self.conversation_manager.get_initial_message()
            st.session_state.conversation_history.append({
                'type': 'system',
                'text': initial_message
            })
            
    def _handle_user_input(self):
        """
        사용자 입력을 처리하고 적절한 응답을 생성합니다.
        """
        # 사용자 입력 받기
        user_input = st.text_input("메시지를 입력하세요:", key="user_input")
        
        if user_input and user_input not in [msg['text'] for msg in st.session_state.conversation_history]:
            # 사용자 입력 기록
            st.session_state.conversation_history.append({
                'type': 'user',
                'text': user_input
            })
            
            # 대화 관리자를 통한 응답 생성
            response = self.conversation_manager.process_user_input(user_input)
            
            # 응답 기록
            st.session_state.conversation_history.append({
                'type': 'system',
                'text': response
            })
            
            # 프로필 업데이트
            st.session_state.user_profile.update(
                self.conversation_manager.get_current_profile()
            )
            
            # 매칭 준비 상태 확인
            if self.conversation_manager.is_profile_complete():
                st.session_state.ready_for_matching = True
                
            # 페이지 리프레시
            st.experimental_rerun()
            
    def _show_matching_results(self):
        """
        사용자 프로필에 가장 적합한 지원사업을 보여줍니다.
        """
        st.write("### 🎯 추천 지원사업")
        st.write("수집된 정보를 바탕으로 가장 적합한 지원사업을 찾았습니다.")
        
        # 매칭 결과 얻기
        matches = self.matcher.find_matches(st.session_state.user_profile)
        
        # 결과 표시
        for idx, match in enumerate(matches, 1):
            with st.expander(f"{idx}. {match['program_name']} (매칭 점수: {match['score']:.2f})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("#### 💡 사업 개요")
                    st.write(match['details']['BSNS_PURPS_CN'])
                    
                    st.write("#### 👥 지원 대상")
                    st.write(match['details']['APPL_TRGET_RM_CN'])
                    
                with col2:
                    st.write("#### 💰 지원 규모")
                    st.metric(
                        label="지원금액",
                        value=f"{match['details']['budget_normalized']:,.0f} 백만원"
                    )
                    
                    st.write("#### 📊 매칭 상세 점수")
                    st.write(f"- 사업 관련성: {match['relevance_score']:.2f}")
                    st.write(f"- 규모 적합도: {match['scale_score']:.2f}")
                    st.write(f"- 요건 부합도: {match['requirement_score']:.2f}")
        
        # 새로운 검색 시작 버튼
        if st.button("새로운 검색 시작"):
            st.session_state.clear()
            st.experimental_rerun()

if __name__ == "__main__":
    app = SportSupportNavigator()
    app.run()

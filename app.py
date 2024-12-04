import streamlit as st
from src.data_processor import DataProcessor
from src.matcher import ProgramMatcher
from src.conversation import ConversationManager

class SportSupportNavigator:
    def __init__(self):
        """
        SportSupportNavigator 초기화
        
        이 클래스는 세 가지 주요 컴포넌트를 통합합니다:
        1. DataProcessor: 지원사업 데이터 전처리
        2. ProgramMatcher: 사용자-지원사업 매칭 엔진
        3. ConversationManager: 대화형 인터페이스 관리
        
        또한 Streamlit 세션 상태를 초기화하여 대화 기록과 사용자 프로필을 유지합니다.
        """
        # 핵심 컴포넌트 초기화
        try:
            self.data_processor = DataProcessor()
            self.processed_data = self.data_processor.preprocess_support_programs()
            self.matcher = ProgramMatcher(self.processed_data)
            self.conversation_manager = ConversationManager()
        except Exception as e:
            st.error(f"시스템 초기화 중 오류가 발생했습니다: {str(e)}")
            return
        
        # Streamlit 세션 상태 초기화
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {}
        if 'ready_for_matching' not in st.session_state:
            st.session_state.ready_for_matching = False

    def run(self):
        """
        메인 애플리케이션 실행
        
        사용자 인터페이스의 세 가지 주요 부분을 관리합니다:
        1. 대화 히스토리 표시
        2. 사용자 입력 처리
        3. 매칭 결과 표시
        """
        # 애플리케이션 헤더
        st.title("Sport Support Navigator")
        st.subheader("스포츠산업 지원사업 지능형 매칭 시스템")
        
        try:
            # 주요 인터페이스 컴포넌트 실행
            self._display_conversation_history()
            self._handle_user_input()
            
            if st.session_state.ready_for_matching:
                self._show_matching_results()
                
        except Exception as e:
            st.error("애플리케이션 실행 중 오류가 발생했습니다. 페이지를 새로고침해 주세요.")
            st.exception(e)

    def _display_conversation_history(self):
        """
        대화 히스토리를 시각적으로 표시합니다.
        
        대화 참여자를 이모지로 구분하여 표시합니다:
        - 🤖 시스템 메시지
        - 👤 사용자 메시지
        """
        # 기존 대화 히스토리 표시
        for message in st.session_state.conversation_history:
            if message['type'] == 'system':
                st.markdown(f"🤖 {message['text']}")
            else:
                st.markdown(f"👤 {message['text']}")
        
        # 첫 대화 시작
        if not st.session_state.conversation_history:
            initial_message = self.conversation_manager.get_initial_message()
            st.session_state.conversation_history.append({
                'type': 'system',
                'text': initial_message
            })

    def _handle_user_input(self):
        try:
            user_input = st.text_input("메시지를 입력하세요:", key="user_input")
            
            if user_input and user_input not in [msg['text'] for msg in st.session_state.conversation_history]:
                # 사용자 입력 처리
                with st.spinner('처리중...'):
                    response = self.conversation_manager.process_user_input(user_input)
                    
                    # 대화 기록 업데이트
                    st.session_state.conversation_history.append({
                        'type': 'user',
                        'text': user_input
                    })
                    st.session_state.conversation_history.append({
                        'type': 'system',
                        'text': response
                    })
                    
                    # 상태 업데이트
                    st.session_state.user_profile = self.conversation_manager.get_current_profile()
                    
                    if self.conversation_manager.is_profile_complete():
                        st.session_state.ready_for_matching = True
                    
                st.rerun()
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            # 로깅 추가
            print(f"Error in _handle_user_input: {e}")

    def _show_matching_results(self):
        """
        사용자 프로필에 가장 적합한 지원사업을 보여줍니다.
        
        각 추천 결과는 다음 정보를 포함합니다:
        1. 사업 개요
        2. 지원 대상
        3. 지원 규모
        4. 매칭 상세 점수
        """
        st.markdown("### 🎯 추천 지원사업")
        st.write("수집된 정보를 바탕으로 가장 적합한 지원사업을 찾았습니다.")
        
        try:
            # 매칭 결과 얻기
            matches = self.matcher.find_matches(st.session_state.user_profile)
            
            # 결과 표시
            for idx, match in enumerate(matches, 1):
                with st.expander(
                    f"{idx}. {match['program_name']} (매칭 점수: {match['score']:.2f})"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 💡 사업 개요")
                        st.write(match['details']['BSNS_PURPS_CN'])
                        
                        st.markdown("#### 👥 지원 대상")
                        st.write(match['details']['APPL_TRGET_RM_CN'])
                        
                    with col2:
                        st.markdown("#### 💰 지원 규모")
                        st.metric(
                            label="지원금액",
                            value=f"{match['details']['budget_normalized']:,.0f} 백만원"
                        )
                        
                        st.markdown("#### 📊 매칭 상세 점수")
                        st.write(f"- 사업 관련성: {match['relevance_score']:.2f}")
                        st.write(f"- 규모 적합도: {match['scale_score']:.2f}")
                        st.write(f"- 요건 부합도: {match['requirement_score']:.2f}")
            
            # 새로운 검색 시작 버튼
            if st.button("새로운 검색 시작"):
                st.session_state.clear()
                st.experimental_rerun()
                
        except Exception as e:
            st.error("매칭 결과를 표시하는 중 오류가 발생했습니다.")
            st.exception(e)

if __name__ == "__main__":
    app = SportSupportNavigator()
    app.run()

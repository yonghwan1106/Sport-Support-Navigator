# 파일 위치: sports-industry-support/app.py
#
# 이 파일은 스포츠산업 지원사업 분석 시스템의 메인 애플리케이션입니다.
# 홈페이지와 전체 앱의 기본 구조를 정의합니다.

import streamlit as st  # 웹 애플리케이션 구현을 위한 라이브러리
from utils import DataHandler  # 데이터 처리를 위한 커스텀 클래스

class SportsSupportApp:
    """
    스포츠산업 지원사업 분석 시스템의 메인 클래스입니다.
    전체 애플리케이션의 구조와 기능을 관리합니다.
    """
    
    def __init__(self):
        """
        애플리케이션을 초기화합니다.
        필요한 데이터를 로드하고 기본 설정을 구성합니다.
        """
        try:
            # 데이터 핸들러 초기화
            self.data_handler = DataHandler()
        except Exception as e:
            # 초기화 중 오류 발생시 사용자에게 알림
            st.error("""
                애플리케이션 초기화 중 오류가 발생했습니다.
                관리자에게 문의해주세요.
                
                오류 내용:
                {}
            """.format(str(e)))
            st.stop()  # 애플리케이션 실행 중단

    def set_page_config(self):
        """
        스트림릿 페이지의 기본 설정을 구성합니다.
        페이지 제목, 아이콘, 레이아웃 등을 설정합니다.
        """
        st.set_page_config(
            page_title="스포츠산업 지원사업 분석 시스템",  # 브라우저 탭에 표시될 제목
            page_icon="🎯",  # 페이지 아이콘
            layout="wide",  # 전체 화면 레이아웃 사용
            initial_sidebar_state="expanded"  # 사이드바 초기 상태
        )
    
    def show_welcome_section(self):
        """
        환영 섹션을 표시합니다.
        시스템의 주요 기능과 사용 방법을 소개합니다.
        """
        try:
            # 메인 제목
            st.title("🎯 스포츠산업 지원사업 분석 시스템")
            
            # 시스템 소개
            st.markdown("""
            이 시스템은 스포츠산업 지원사업의 자격요건과 지원기업 정보를 종합적으로 분석하여 
            의미 있는 인사이트를 제공합니다.
            
            ### 주요 기능
            - 📋 **지원사업 검색**: 기업 조건에 맞는 지원사업을 쉽게 찾아보세요
            - 📊 **기업 분석**: 지원기업들의 특성과 분포를 파악해보세요
            - 📈 **트렌드 분석**: 시계열적 변화와 패턴을 확인해보세요
            
            왼쪽 사이드바의 메뉴를 통해 각 기능을 이용하실 수 있습니다.
            """)
        except Exception as e:
            st.error(f"환영 섹션 표시 중 오류 발생: {str(e)}")

    def show_key_metrics(self):
        """
        주요 지표들을 표시합니다.
        전체 지원사업 수, 참여 기업 수 등의 핵심 정보를 보여줍니다.
        """
        try:
            # 로딩 상태 표시
            with st.spinner('주요 지표를 불러오는 중...'):
                # 필요한 데이터 가져오기
                qual_df = self.data_handler.get_qualification_data()
                company_df = self.data_handler.get_company_data()
                
                # 4개의 컬럼으로 지표 표시
                col1, col2, col3, col4 = st.columns(4)
                
                # 총 지원사업 수
                with col1:
                    st.metric(
                        "총 지원사업 수",
                        f"{len(qual_df['BSNS_TASK_NM'].unique()):,}개"
                    )
                
                # 참여 기업 수
                with col2:
                    st.metric(
                        "참여 기업 수",
                        f"{len(company_df['CMPNY_NM'].unique()):,}개"
                    )
                
                # 평균 지원금액
                with col3:
                    avg_amount = qual_df['APPL_SCALE_TOT_BUDGET_PRICE'].mean()
                    st.metric(
                        "평균 지원금액",
                        f"{avg_amount:,.0f}원"
                    )

                # 지원기업 분포 지역 수 계산 및 표시
                with col4:
                    # 주소에서 첫 번째 단어(시/도)를 추출하여 고유한 개수 계산
                    unique_regions = company_df['CMPNY_ADDR'].str.split().str[0].nunique()
                    st.metric(
                        "지원기업 분포 지역",
                        f"{unique_regions}개 지역"
                    )
                    
        except Exception as e:
            # 오류 발생시 사용자에게 알림
            st.error(f"주요 지표 표시 중 오류 발생: {str(e)}")

    def show_recent_updates(self):
        """
        최근 업데이트된 지원사업 정보를 표시합니다.
        가장 최근에 공고된 지원사업들을 보여줍니다.
        """
        try:
            # 제목 표시
            st.subheader("최근 공고 지원사업")
            
            # 데이터 가져오기
            qual_df = self.data_handler.get_qualification_data()
            
            # 최근 공고 순으로 정렬
            recent_programs = qual_df.sort_values(
                'RCRIT_PD_BEGIN_DE',  # 모집 시작일 기준
                ascending=False  # 최신순 정렬
            ).head(5)  # 상위 5개만 선택
            
            # 표시할 컬럼 선택 및 이름 변경
            display_cols = {
                'BSNS_TASK_NM': '사업명',
                'RCRIT_PD_BEGIN_DE': '접수 시작일',
                'RCRIT_PD_END_DE': '접수 마감일',
                'APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE': '지원금액'
            }
            
            # 데이터프레임 표시
            st.dataframe(
                recent_programs[display_cols.keys()].rename(columns=display_cols),
                use_container_width=True,  # 전체 너비 사용
                hide_index=True  # 인덱스 숨김
            )
            
        except Exception as e:
            st.error(f"최근 업데이트 표시 중 오류 발생: {str(e)}")

    def show_data_overview(self):
        """
        데이터 현황 개요를 표시합니다.
        전체 데이터의 기본 통계와 특성을 보여줍니다.
        """
        try:
            # 제목 표시
            st.subheader("데이터 현황")
            
            # 2개 컬럼으로 구성
            col1, col2 = st.columns(2)
            
            # 왼쪽 컬럼: 지원사업 자격요건 데이터 현황
            with col1:
                st.markdown("#### 지원사업 자격요건 데이터")
                qual_df = self.data_handler.get_qualification_data()
                
                # 기본 통계 표시
                st.write(f"- 데이터 기간: {qual_df['APPL_YEAR'].min()} ~ {qual_df['APPL_YEAR'].max()}")
                st.write(f"- 총 레코드 수: {len(qual_df):,}개")
                st.write(f"- 지원분야 수: {qual_df['APPL_REALM_NM'].nunique()}개")
            
            # 오른쪽 컬럼: 지원기업 정보 데이터 현황
            with col2:
                st.markdown("#### 지원기업 정보 데이터")
                company_df = self.data_handler.get_company_data()
                
                # 기업 관련 통계 표시
                st.write(f"- 총 기업 수: {len(company_df['CMPNY_NM'].unique()):,}개")
                st.write(f"- 업종 수: {company_df['INDUTY_NM'].nunique()}개")
                st.write(f"- 평균 업력: {company_df['업력'].mean():.1f}년")
                
        except Exception as e:
            st.error(f"데이터 현황 표시 중 오류 발생: {str(e)}")

    def run(self):
        """
        애플리케이션을 실행합니다.
        모든 섹션을 순차적으로 표시하고 오류를 처리합니다.
        """
        try:
            # 기본 페이지 설정
            self.set_page_config()
            
            # 환영 섹션 표시
            self.show_welcome_section()
            
            # 구분선 추가
            st.divider()
            
            # 주요 지표 표시
            self.show_key_metrics()
            
            # 구분선 추가
            st.divider()
            
            # 최근 업데이트와 데이터 현황을 나란히 표시
            col1, col2 = st.columns([2, 1])  # 2:1 비율로 분할
            
            with col1:
                self.show_recent_updates()
                
            with col2:
                self.show_data_overview()
                
        except Exception as e:
            # 예상치 못한 오류 발생시 사용자에게 알림
            st.error(f"""
                애플리케이션 실행 중 예상치 못한 오류가 발생했습니다.
                관리자에게 문의해주세요.
                
                오류 내용:
                {str(e)}
            """)

def main():
    """
    메인 함수입니다.
    애플리케이션을 초기화하고 실행합니다.
    """
    try:
        # 애플리케이션 인스턴스 생성 및 실행
        app = SportsSupportApp()
        app.run()
    except Exception as e:
        # 시작 단계에서 오류 발생시 알림
        st.error(f"애플리케이션 시작 실패: {str(e)}")

# 스크립트가 직접 실행될 때만 main() 함수 호출
if __name__ == "__main__":
    main()

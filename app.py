# 파일 위치: sports-industry-support/app.py

import streamlit as st
import pandas as pd
import numpy as np
from utils import DataHandler

# 페이지 설정을 가장 먼저 실행
st.set_page_config(
    page_title="스포츠산업 지원사업 분석 시스템",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_clean_company_age(company_df):
    """업력 데이터를 정제하고 계산합니다."""
    try:
        # 숫자형으로 변환
        company_df['업력'] = pd.to_numeric(company_df['업력'], errors='coerce')
        
        # 이상치 제거
        company_df.loc[company_df['업력'] > 50, '업력'] = np.nan
        company_df.loc[company_df['업력'] < 0, '업력'] = np.nan
        
        # 유효한 업력 데이터만의 평균 계산
        valid_age = company_df['업력'].dropna()
        return valid_age.mean() if not valid_age.empty else 0
        
    except Exception:
        return 0

def get_valid_company_count(company_df):
    """유효한 참여 기업 수를 계산합니다."""
    try:
        # 기업명이 있는 경우만 카운트
        valid_companies = company_df['CMPNY_NM'].dropna().unique()
        return len(valid_companies)
    except Exception:
        return 0

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
            st.error(f"""
                애플리케이션 초기화 중 오류가 발생했습니다.
                관리자에게 문의해주세요.
                
                오류 내용:
                {str(e)}
            """)
            st.stop()
    
    def log_data_quality(self, company_df):
        """데이터 품질 정보를 로깅합니다."""
        try:
            total_records = len(company_df)
            valid_companies = len(company_df['CMPNY_NM'].dropna())
            valid_ages = len(company_df['업력'].dropna())
            
            st.sidebar.markdown("### 데이터 품질 정보")
            st.sidebar.write(f"총 레코드 수: {total_records:,}")
            st.sidebar.write(f"유효한 기업명 수: {valid_companies:,}")
            st.sidebar.write(f"유효한 업력 데이터 수: {valid_ages:,}")
        except Exception as e:
            st.error(f"데이터 품질 로깅 중 오류: {str(e)}")
    
    def show_welcome_section(self):
        """
        환영 섹션을 표시합니다.
        시스템의 주요 기능과 사용 방법을 소개합니다.
        """
        try:
            st.title("🎯 스포츠산업 지원사업 분석 시스템")
            
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
        """주요 지표들을 표시합니다."""
        try:
            with st.spinner('주요 지표를 불러오는 중...'):
                # 데이터 로드
                qual_df = self.data_handler.get_qualification_data()
                company_df = self.data_handler.get_company_data()
                
                # 데이터 품질 로깅
                self.log_data_quality(company_df)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "총 지원사업 수",
                        f"{len(qual_df['BSNS_TASK_NM'].unique()):,}개"
                    )
                
                with col2:
                    valid_company_count = get_valid_company_count(company_df)
                    st.metric(
                        "참여 기업 수",
                        f"{valid_company_count:,}개"
                    )
                
                with col3:
                    avg_amount = qual_df['APPL_SCALE_TOT_BUDGET_PRICE'].mean()
                    st.metric(
                        "평균 지원금액",
                        f"{avg_amount:,.0f}원"
                    )
                
                with col4:
                    unique_regions = company_df['지역'].dropna().nunique()
                    st.metric(
                        "지원기업 분포 지역",
                        f"{unique_regions}개 지역"
                    )
                    
        except Exception as e:
            st.error(f"주요 지표 표시 중 오류 발생: {str(e)}")

    def show_recent_updates(self):
        """최근 업데이트된 지원사업 정보를 표시합니다."""
        try:
            st.subheader("최근 공고 지원사업")
            qual_df = self.data_handler.get_qualification_data()
            
            recent_programs = qual_df.sort_values(
                'RCRIT_PD_BEGIN_DE',
                ascending=False
            ).head(5)
            
            display_cols = {
                'BSNS_TASK_NM': '사업명',
                'RCRIT_PD_BEGIN_DE': '접수 시작일',
                'RCRIT_PD_END_DE': '접수 마감일',
                'APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE': '지원금액'
            }
            
            st.dataframe(
                recent_programs[display_cols.keys()].rename(columns=display_cols),
                use_container_width=True,
                hide_index=True
            )
            
        except Exception as e:
            st.error(f"최근 업데이트 표시 중 오류 발생: {str(e)}")

    def show_data_overview(self):
        """데이터 현황 개요를 표시합니다."""
        try:
            st.subheader("데이터 현황")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 지원사업 자격요건 데이터")
                qual_df = self.data_handler.get_qualification_data()
                st.write(f"- 데이터 기간: {qual_df['APPL_YEAR'].min()} ~ {qual_df['APPL_YEAR'].max()}")
                st.write(f"- 총 레코드 수: {len(qual_df):,}개")
                st.write(f"- 지원분야 수: {qual_df['APPL_REALM_NM'].nunique()}개")
            
            with col2:
                st.markdown("#### 지원기업 정보 데이터")
                company_df = self.data_handler.get_company_data()
                avg_age = get_clean_company_age(company_df)
                st.write(f"- 총 기업 수: {get_valid_company_count(company_df):,}개")
                st.write(f"- 업종 수: {company_df['INDUTY_NM'].dropna().nunique()}개")
                st.write(f"- 평균 업력: {avg_age:.1f}년")
                
        except Exception as e:
            st.error(f"데이터 현황 표시 중 오류 발생: {str(e)}")

    def run(self):
        """애플리케이션을 실행합니다."""
        try:
            self.show_welcome_section()
            st.divider()
            self.show_key_metrics()
            st.divider()
            
            col1, col2 = st.columns([2, 1])
            with col1:
                self.show_recent_updates()
            with col2:
                self.show_data_overview()
                
        except Exception as e:
            st.error(f"""
                애플리케이션 실행 중 예상치 못한 오류가 발생했습니다.
                관리자에게 문의해주세요.
                
                오류 내용:
                {str(e)}
            """)

def main():
    """메인 함수입니다."""
    try:
        app = SportsSupportApp()
        app.run()
    except Exception as e:
        st.error(f"애플리케이션 시작 실패: {str(e)}")

if __name__ == "__main__":
    main()

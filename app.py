# app.py

import streamlit as st
from pathlib import Path
import sys

# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# utils.py에서 데이터 핸들러 임포트
from utils import DataHandler

class SportsSupportApp:
    def __init__(self):
        """애플리케이션을 초기화하고 기본 설정을 구성합니다."""
        # 데이터 파일 경로 설정
        self.data_path = current_dir / 'data'
        # 데이터 핸들러 초기화 (경로 전달)
        self.data_handler = DataHandler(self.data_path)
        
    def set_page_config(self):
        """페이지의 기본 구성을 설정합니다."""
        st.set_page_config(
            page_title="스포츠산업 지원사업 분석 시스템",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def show_welcome_section(self):
        """환영 섹션을 표시합니다."""
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

    def show_key_metrics(self):
        """주요 지표들을 표시합니다."""
        # 데이터 가져오기
        qual_df = self.data_handler.get_qualification_data()
        company_df = self.data_handler.get_company_data()
        
        # 주요 지표 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "총 지원사업 수",
                f"{len(qual_df['BSNS_TASK_NM'].unique()):,}개"
            )
        
        with col2:
            st.metric(
                "참여 기업 수",
                f"{len(company_df['CMPNY_NM'].unique()):,}개"
            )
        
        with col3:
            avg_amount = qual_df['APPL_SCALE_TOT_BUDGET_PRICE'].mean()
            st.metric(
                "평균 지원금액",
                f"{avg_amount:,.0f}원"
            )
        
        with col4:
            unique_regions = company_df['CMPNY_ADDR'].str.split().str[0].nunique()
            st.metric(
                "지원기업 분포 지역",
                f"{unique_regions}개 지역"
            )

    def show_recent_updates(self):
        """최근 업데이트된 지원사업 정보를 표시합니다."""
        qual_df = self.data_handler.get_qualification_data()
        
        st.subheader("최근 공고 지원사업")
        
        # 최근 공고 순으로 정렬
        recent_programs = qual_df.sort_values(
            'RCRIT_PD_BEGIN_DE', 
            ascending=False
        ).head(5)
        
        # 표시할 컬럼 선택 및 이름 변경
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

    def show_data_overview(self):
        """데이터 현황 개요를 표시합니다."""
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
            st.write(f"- 총 기업 수: {len(company_df['CMPNY_NM'].unique()):,}개")
            st.write(f"- 업종 수: {company_df['INDUTY_NM'].nunique()}개")
            st.write(f"- 평균 업력: {company_df['업력'].mean():.1f}년")

    def run(self):
        """애플리케이션을 실행합니다."""
        self.set_page_config()
        self.show_welcome_section()
        
        # 구분선 추가
        st.divider()
        
        # 주요 지표 표시
        self.show_key_metrics()
        
        # 구분선 추가
        st.divider()
        
        # 최근 업데이트 및 데이터 현황
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.show_recent_updates()
            
        with col2:
            self.show_data_overview()

def main():
    app = SportsSupportApp()
    app.run()

if __name__ == "__main__":
    main()

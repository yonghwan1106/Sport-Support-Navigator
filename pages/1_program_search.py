# pages/1_program_search.py

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import plotly.express as px

# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# utils.py의 데이터 핸들러 임포트
from utils import DataHandler

def format_amount(amount):
    """금액을 읽기 쉬운 한국어 형식으로 변환합니다"""
    if pd.isna(amount):
        return "미정"
    
    amount = float(amount)
    if amount >= 100000000:
        return f"{amount/100000000:.1f}억원"
    elif amount >= 10000:
        return f"{amount/10000:.0f}만원"
    else:
        return f"{amount:,.0f}원"

def main():
    st.set_page_config(page_title="지원사업 자격요건 검색", layout="wide")
    
    # 페이지 제목
    st.title("💡 지원사업 자격요건 검색")
    st.markdown("기업 조건에 맞는 지원사업을 찾아보세요.")
    
    # 데이터 핸들러 초기화
    data_handler = DataHandler(root_dir / 'data')
    
    # 사이드바에 검색 필터 구성
    with st.sidebar:
        st.header("검색 필터")
        
        # 지원 년도 선택
        years = data_handler.get_available_years()
        selected_year = st.selectbox(
            "지원년도",
            options=sorted(years, reverse=True),
            index=0
        )
        
        # 지원 분야 선택
        categories = data_handler.get_support_categories()
        selected_categories = st.multiselect(
            "지원분야",
            options=categories,
            default=None
        )
        
        # 기업 조건 입력
        st.subheader("기업 조건")
        company_age = st.number_input(
            "기업 업력(년)",
            min_value=0,
            max_value=100,
            value=0
        )
        
        is_startup = st.checkbox("예비창업자 여부")
        
        support_amount = st.slider(
            "희망 지원금액(억원)",
            min_value=0,
            max_value=100,
            value=(0, 100)
        )

    # 메인 영역 구성
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 검색 결과 표시
        st.subheader("검색 결과")
        
        # 데이터 필터링
        filtered_df = data_handler.filter_qualifications(
            year=selected_year,
            categories=selected_categories,
            company_age=company_age,
            is_startup=is_startup,
            min_amount=support_amount[0]*100000000,
            max_amount=support_amount[1]*100000000
        )
        
        if len(filtered_df) == 0:
            st.warning("검색 조건에 맞는 지원사업이 없습니다.")
        else:
            # 중요 컬럼만 선택하여 표시
            display_cols = [
                'BSNS_TASK_NM',         # 사업과제명
                'APPL_YEAR',            # 지원년도
                'RCRIT_PD_BEGIN_DE',    # 모집시작일
                'RCRIT_PD_END_DE',      # 모집종료일
                'APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE'  # 최대지원금액
            ]
            
            # 날짜 형식 변환
            for date_col in ['RCRIT_PD_BEGIN_DE', 'RCRIT_PD_END_DE']:
                filtered_df[date_col] = pd.to_datetime(
                    filtered_df[date_col], 
                    format='%Y%m%d'
                ).dt.strftime('%Y-%m-%d')
            
            # 금액 형식 변환
            filtered_df['지원금액'] = filtered_df[
                'APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE'
            ].apply(format_amount)
            
            # 표시할 데이터 정리
            display_df = filtered_df[display_cols].copy()
            display_df.columns = [
                '사업명', '년도', '모집시작일', '모집종료일', '지원금액'
            ]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
    with col2:
        # 통계 및 시각화
        st.subheader("지원사업 통계")
        
        if len(filtered_df) > 0:
            # 평균 지원금액 계산
            avg_amount = filtered_df[
                'APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE'
            ].mean()
            
            # 주요 지표 표시
            st.metric(
                "검색된 사업 수", 
                f"{len(filtered_df)}개"
            )
            st.metric(
                "평균 지원금액",
                format_amount(avg_amount)
            )
            
            # 지원금액 분포 시각화
            fig = px.box(
                filtered_df,
                y='APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE',
                title='지원금액 분포'
            )
            fig.update_layout(
                yaxis_title='지원금액(원)',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()

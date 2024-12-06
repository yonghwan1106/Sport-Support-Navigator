# 파일 위치: sports-industry-support/pages/2_company_analysis.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from utils import DataHandler

def ensure_numeric(df, column):
    """
    데이터프레임의 특정 컬럼을 숫자형으로 변환합니다.
    변환할 수 없는 값은 NaN으로 처리됩니다.
    
    매개변수:
        df (DataFrame): 처리할 데이터프레임
        column (str): 변환할 컬럼명
    """
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df

def create_industry_distribution_chart(df):
    """업종별 기업 분포를 도넛 차트로 시각화합니다."""
    # 결측치 제외하고 업종별 기업 수 계산
    industry_counts = df['INDUTY_NM'].dropna().value_counts()
    
    fig = px.pie(
        values=industry_counts.values,
        names=industry_counts.index,
        title='업종별 기업 분포',
        hole=0.4
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_region_distribution_chart(df):
    """지역별 기업 분포를 막대 차트로 시각화합니다."""
    # 결측치 제외하고 지역별 기업 수 계산
    region_counts = df['지역'].dropna().value_counts()
    
    fig = px.bar(
        x=region_counts.index,
        y=region_counts.values,
        title='지역별 기업 분포',
        labels={'x': '지역', 'y': '기업 수'}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="기업 분석",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 지원기업 특성 분석")
    st.markdown("""
        이 페이지에서는 스포츠산업 지원사업에 참여한 기업들의 특성을 분석합니다.
        업종, 지역, 규모 등 다양한 측면에서 기업들의 특징을 살펴볼 수 있습니다.
    """)

    try:
        # 데이터 핸들러 초기화
        data_handler = DataHandler()
        company_df = data_handler.get_company_data()
        
        # 연도 컬럼을 숫자형으로 변환
        company_df = ensure_numeric(company_df, 'APPL_YEAR')
        company_df = ensure_numeric(company_df, '업력')

        # 사이드바 필터 구성
        with st.sidebar:
            st.header("분석 필터")
            
            # 연도 선택 (결측치 제외)
            years = sorted(
                company_df['APPL_YEAR'].dropna().unique().astype(int),
                reverse=True
            )
            selected_year = st.selectbox(
                "분석 년도",
                options=years,
                format_func=lambda x: f"{int(x)}년"
            )
            
            # 업종 선택 (결측치 제외)
            industries = ['전체'] + sorted(
                company_df['INDUTY_NM'].dropna().unique()
            )
            selected_industry = st.selectbox(
                "업종",
                options=industries
            )

        # 데이터 필터링
        filtered_df = company_df.copy()
        
        # 연도 필터링 (숫자형으로 비교)
        if selected_year:
            filtered_df = filtered_df[
                filtered_df['APPL_YEAR'].astype(float) == float(selected_year)
            ]
            
        # 업종 필터링
        if selected_industry != '전체':
            filtered_df = filtered_df[
                filtered_df['INDUTY_NM'] == selected_industry
            ]

        # 주요 지표 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "총 기업 수",
                f"{len(filtered_df):,}개"
            )
        
        with col2:
            avg_age = filtered_df['업력'].mean()
            st.metric(
                "평균 업력",
                f"{avg_age:.1f}년" if pd.notna(avg_age) else "정보없음"
            )
        
        with col3:
            unique_regions = filtered_df['지역'].dropna().nunique()
            st.metric(
                "분포 지역 수",
                f"{unique_regions}개 지역"
            )
        
        with col4:
            mode_result = filtered_df['INDUTY_NM'].mode()
            top_industry = mode_result[0] if len(mode_result) > 0 else "정보없음"
            st.metric(
                "주요 업종",
                top_industry
            )


        # 상세 분석 섹션
        st.header("상세 분석")
        
        # 분석 탭 구성
        tab1, tab2, tab3 = st.tabs(["업종 분석", "지역 분석", "상세 데이터"])
        
        with tab1:
            st.subheader("업종별 분포")
            industry_fig = create_industry_distribution_chart(filtered_df)
            st.plotly_chart(industry_fig, use_container_width=True)
            
            # 업종별 추가 분석
            st.subheader("업종별 평균 업력")
            industry_age = filtered_df.groupby('INDUTY_NM')['업력'].mean()
            
            fig = px.bar(
                x=industry_age.index,
                y=industry_age.values,
                labels={'x': '업종', 'y': '평균 업력(년)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("지역별 분포")
            region_fig = create_region_distribution_chart(filtered_df)
            st.plotly_chart(region_fig, use_container_width=True)
            
            # 지역별 추가 분석
            st.subheader("상위 10개 지역의 업종 분포")
            top_regions = filtered_df.groupby('지역').size().nlargest(10).index
            region_industry = pd.crosstab(
                filtered_df[filtered_df['지역'].isin(top_regions)]['지역'],
                filtered_df[filtered_df['지역'].isin(top_regions)]['INDUTY_NM']
            )
            
            fig = px.bar(
                region_industry,
                barmode='stack',
                labels={'value': '기업 수', 'index': '지역'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("기업 상세 정보")
            
            # 검색 필터
            search_term = st.text_input("기업명 검색")
            
            # 데이터 필터링
            if search_term:
                display_df = filtered_df[
                    filtered_df['CMPNY_NM'].str.contains(search_term, na=False)
                ]
            else:
                display_df = filtered_df
            
            # 표시할 컬럼 선택
            display_columns = [
                'CMPNY_NM', 'RPRSNTV_NM', 'INDUTY_NM',
                'CMPNY_ADDR', 'BSNS_NO', 'APPL_YEAR'
            ]
            
            # 컬럼명 한글화
            column_mapping = {
                'CMPNY_NM': '기업명',
                'RPRSNTV_NM': '대표자명',
                'INDUTY_NM': '업종',
                'CMPNY_ADDR': '주소',
                'BSNS_NO': '사업자번호',
                'APPL_YEAR': '지원년도'
            }
            
            # 데이터프레임 표시
            display_df = display_df[display_columns].rename(columns=column_mapping)
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
    except Exception as e:
        st.error(f"""
            데이터 처리 중 오류가 발생했습니다.
            관리자에게 문의해주세요.
            
            오류 내용:
            {str(e)}
            
            데이터 상태:
            {company_df.dtypes if 'company_df' in locals() else '데이터 로드 실패'}
        """)
        # 디버깅을 위한 추가 정보 표시
        st.write("데이터 샘플:")
        if 'company_df' in locals():
            st.write(company_df.head())

if __name__ == "__main__":
    main()

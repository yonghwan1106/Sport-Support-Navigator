# pages/2_company_analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from utils import DataHandler

def create_industry_distribution_chart(df):
    """업종별 기업 분포를 시각화합니다."""
    industry_counts = df['INDUTY_NM'].value_counts()
    
    fig = px.pie(
        values=industry_counts.values,
        names=industry_counts.index,
        title='업종별 기업 분포',
        hole=0.4  # 도넛 차트 스타일
    )
    return fig

def create_region_map(df):
    """지역별 기업 분포를 시각화합니다."""
    region_counts = df['CMPNY_ADDR'].str.split().str[0].value_counts()
    
    fig = go.Figure(data=go.Choropleth(
        locations=region_counts.index,
        z=region_counts.values,
        locationmode='country names',
        colorscale='Viridis',
        colorbar_title='기업 수'
    ))
    
    fig.update_layout(
        title='지역별 기업 분포',
        geo_scope='asia',  # 한국 중심으로 보기
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

    # 데이터 핸들러 초기화
    data_handler = DataHandler(root_dir / 'data')
    company_df = data_handler.get_company_data()

    # 사이드바 필터 구성
    with st.sidebar:
        st.header("분석 필터")
        
        # 연도 선택
        years = sorted(company_df['APPL_YEAR'].unique(), reverse=True)
        selected_year = st.selectbox(
            "분석 년도",
            options=years
        )
        
        # 업종 선택
        industries = ['전체'] + sorted(company_df['INDUTY_NM'].unique())
        selected_industry = st.selectbox(
            "업종",
            options=industries
        )

    # 데이터 필터링
    filtered_df = company_df.copy()
    if selected_year:
        filtered_df = filtered_df[filtered_df['APPL_YEAR'] == selected_year]
    if selected_industry != '전체':
        filtered_df = filtered_df[filtered_df['INDUTY_NM'] == selected_industry]

    # 주요 지표 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "총 기업 수",
            f"{len(filtered_df):,}개"
        )
    
    with col2:
        avg_age = filtered_df['BSNS_NO'].str[:4].astype(int).mean()
        st.metric(
            "평균 업력",
            f"{2024 - avg_age:.1f}년"
        )
    
    with col3:
        unique_regions = filtered_df['CMPNY_ADDR'].str.split().str[0].nunique()
        st.metric(
            "분포 지역 수",
            f"{unique_regions}개 지역"
        )
    
    with col4:
        top_industry = filtered_df['INDUTY_NM'].mode()[0]
        st.metric(
            "주요 업종",
            f"{top_industry}"
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
        industry_age = filtered_df.groupby('INDUTY_NM').apply(
            lambda x: 2024 - x['BSNS_NO'].str[:4].astype(int).mean()
        ).sort_values(ascending=False)
        
        fig = px.bar(
            x=industry_age.index,
            y=industry_age.values,
            labels={'x': '업종', 'y': '평균 업력(년)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("지역별 분포")
        region_fig = create_region_map(filtered_df)
        st.plotly_chart(region_fig, use_container_width=True)
        
        # 지역별 추가 분석
        st.subheader("상위 10개 지역")
        top_regions = filtered_df['CMPNY_ADDR'].str.split().str[0].value_counts().head(10)
        fig = px.bar(
            x=top_regions.index,
            y=top_regions.values,
            labels={'x': '지역', 'y': '기업 수'}
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
        
        display_df = display_df[display_columns].rename(columns=column_mapping)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()

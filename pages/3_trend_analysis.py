# pages/3_trend_analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from utils import DataHandler

def create_yearly_support_trend(df):
    """연도별 지원금액 추이를 시각화합니다."""
    yearly_stats = df.groupby('APPL_YEAR').agg({
        'APPL_SCALE_TOT_BUDGET_PRICE': ['mean', 'sum'],
        'APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE': 'mean'
    }).round(2)
    
    # 복합 그래프 생성
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 총 지원금액 추이 (막대 그래프)
    fig.add_trace(
        go.Bar(
            x=yearly_stats.index,
            y=yearly_stats[('APPL_SCALE_TOT_BUDGET_PRICE', 'sum')],
            name="총 지원금액",
            marker_color='lightblue'
        ),
        secondary_y=False
    )
    
    # 평균 지원금액 추이 (선 그래프)
    fig.add_trace(
        go.Scatter(
            x=yearly_stats.index,
            y=yearly_stats[('APPL_SCALE_TOT_BUDGET_PRICE', 'mean')],
            name="평균 지원금액",
            line=dict(color='red')
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title="연도별 지원금액 추이",
        xaxis_title="연도",
        barmode='group'
    )
    
    fig.update_yaxes(title_text="총 지원금액", secondary_y=False)
    fig.update_yaxes(title_text="평균 지원금액", secondary_y=True)
    
    return fig

def analyze_qualification_changes(df):
    """자격요건의 변화 추이를 분석합니다."""
    # 연도별 주요 자격요건 변화 추적
    yearly_quals = df.groupby('APPL_YEAR').agg({
        'APPL_TRGET_PREPFNTN_AT': 'mean',  # 예비창업 대상 비율
        'APPL_TRGET_GRP_POSBL_AT': 'mean', # 단체가능 비율
        'APPL_TRGET_INDVDL_POSBL_AT': 'mean' # 개인가능 비율
    }).round(2)
    
    fig = px.line(
        yearly_quals,
        labels={
            'APPL_TRGET_PREPFNTN_AT': '예비창업 대상',
            'APPL_TRGET_GRP_POSBL_AT': '단체가능',
            'APPL_TRGET_INDVDL_POSBL_AT': '개인가능'
        },
        title='자격요건 변화 추이'
    )
    
    return fig

def create_company_participation_trend(df):
    """기업 참여 트렌드를 분석합니다."""
    yearly_companies = df.groupby(['APPL_YEAR', 'INDUTY_NM']).size().unstack()
    
    fig = px.area(
        yearly_companies,
        title='업종별 참여기업 수 변화',
        labels={'value': '기업 수', 'APPL_YEAR': '연도'}
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="트렌드 분석",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 스포츠산업 지원사업 트렌드 분석")
    st.markdown("""
        이 페이지에서는 스포츠산업 지원사업의 시계열적 변화를 분석합니다.
        지원금액, 자격요건, 기업 참여 등 다양한 측면에서의 트렌드를 확인할 수 있습니다.
    """)

    # 데이터 핸들러 초기화
    data_handler = DataHandler(root_dir / 'data')
    qualifications_df = data_handler.get_qualification_data()
    company_df = data_handler.get_company_data()

    # 트렌드 분석 섹션
    st.header("지원사업 트렌드")
    
    # 지원금액 트렌드
    support_trend_fig = create_yearly_support_trend(qualifications_df)
    st.plotly_chart(support_trend_fig, use_container_width=True)
    
    # 주요 변화 지표
    col1, col2, col3 = st.columns(3)
    
    with col1:
        year_growth = qualifications_df.groupby('APPL_YEAR')[
            'APPL_SCALE_TOT_BUDGET_PRICE'
        ].mean().pct_change().iloc[-1]
        
        st.metric(
            "전년 대비 평균 지원금액 증가율",
            f"{year_growth:.1%}"
        )
    
    with col2:
        total_programs = len(qualifications_df['BSNS_TASK_NM'].unique())
        st.metric(
            "총 지원사업 수",
            f"{total_programs}개"
        )
    
    with col3:
        avg_support = qualifications_df['APPL_SCALE_TOT_BUDGET_PRICE'].mean()
        st.metric(
            "평균 지원금액",
            f"{avg_support:,.0f}원"
        )

    # 자격요건 변화 분석
    st.header("자격요건 변화 분석")
    quals_change_fig = analyze_qualification_changes(qualifications_df)
    st.plotly_chart(quals_change_fig, use_container_width=True)
    
    # 설명 추가
    st.markdown("""
        위 그래프는 각 자격요건 항목의 연도별 변화를 보여줍니다:
        - 예비창업 대상: 예비창업자 지원 가능 여부
        - 단체가능: 단체/기관 지원 가능 여부
        - 개인가능: 개인 지원 가능 여부
    """)

    # 기업 참여 트렌드
    st.header("기업 참여 트렌드")
    company_trend_fig = create_company_participation_trend(company_df)
    st.plotly_chart(company_trend_fig, use_container_width=True)
    
    # 상세 통계
    st.header("상세 통계")
    
    tab1, tab2 = st.tabs(["연도별 통계", "업종별 통계"])
    
    with tab1:
        yearly_stats = qualifications_df.groupby('APPL_YEAR').agg({
            'BSNS_TASK_NM': 'count',
            'APPL_SCALE_TOT_BUDGET_PRICE': ['mean', 'sum']
        }).round(2)
        
        st.dataframe(
            yearly_stats,
            use_container_width=True
        )
    
    with tab2:
        industry_stats = company_df.groupby('INDUTY_NM').agg({
            'CMPNY_NM': 'count',
            'APPL_YEAR': ['min', 'max']
        }).round(2)
        
        st.dataframe(
            industry_stats,
            use_container_width=True
        )

if __name__ == "__main__":
    main()

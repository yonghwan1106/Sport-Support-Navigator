# 파일 위치: sports-industry-support/pages/3_trend_analysis.py
#
# 이 파일은 스포츠산업 지원사업의 시계열적 변화를 분석하고 시각화하는
# 트렌드 분석 페이지를 구현합니다.

import streamlit as st
import pandas as pd
import numpy as np
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
    """
    연도별 지원금액 추이를 복합 그래프로 시각화합니다.
    
    매개변수:
        df (DataFrame): 지원사업 데이터
        
    반환값:
        plotly Figure: 연도별 지원금액 추이 그래프
    """
    try:
        # 숫자형으로 변환
        df['APPL_YEAR'] = pd.to_numeric(df['APPL_YEAR'], errors='coerce')
        df['APPL_SCALE_TOT_BUDGET_PRICE'] = pd.to_numeric(
            df['APPL_SCALE_TOT_BUDGET_PRICE'], 
            errors='coerce'
        )
        
        # 연도별 통계 계산
        yearly_stats = df.groupby('APPL_YEAR').agg({
            'APPL_SCALE_TOT_BUDGET_PRICE': ['mean', 'sum']
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
        
        # 그래프 레이아웃 설정
        fig.update_layout(
            title="연도별 지원금액 추이",
            xaxis_title="연도",
            barmode='group'
        )
        
        fig.update_yaxes(title_text="총 지원금액(원)", secondary_y=False)
        fig.update_yaxes(title_text="평균 지원금액(원)", secondary_y=True)
        
        return fig
        
    except Exception as e:
        st.error(f"지원금액 추이 차트 생성 중 오류 발생: {str(e)}")
        return None

def create_participation_trend(df):
    """
    기업 참여 트렌드를 시각화합니다.
    
    매개변수:
        df (DataFrame): 기업 정보 데이터
        
    반환값:
        plotly Figure: 참여 트렌드 그래프
    """
    try:
        # 숫자형으로 변환
        df['APPL_YEAR'] = pd.to_numeric(df['APPL_YEAR'], errors='coerce')
        
        # 연도별, 업종별 기업 수 계산
        yearly_counts = pd.crosstab(df['APPL_YEAR'], df['INDUTY_NM'])
        
        # 누적 영역 차트 생성
        fig = px.area(
            yearly_counts,
            title='업종별 참여기업 수 변화',
            labels={'value': '기업 수', 'APPL_YEAR': '연도'}
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
        
    except Exception as e:
        st.error(f"참여 트렌드 차트 생성 중 오류 발생: {str(e)}")
        return None

def main():
    # 페이지 기본 설정
    st.set_page_config(
        page_title="트렌드 분석",
        page_icon="📈",
        layout="wide"
    )
    
    # 페이지 제목과 설명
    st.title("📈 스포츠산업 지원사업 트렌드 분석")
    st.markdown("""
        이 페이지에서는 스포츠산업 지원사업의 시계열적 변화를 분석합니다.
        지원금액, 자격요건, 기업 참여 등 다양한 측면에서의 트렌드를 확인할 수 있습니다.
    """)

    try:
        # 데이터 핸들러 초기화
        data_handler = DataHandler()
        
        # 데이터 로드
        quals_df = data_handler.get_qualification_data()
        company_df = data_handler.get_company_data()
        
        # 데이터 전처리
        for df in [quals_df, company_df]:
            if 'APPL_YEAR' in df.columns:
                df['APPL_YEAR'] = pd.to_numeric(df['APPL_YEAR'], errors='coerce')

        # 트렌드 분석 섹션
        st.header("지원사업 트렌드")
        
        # 지원금액 트렌드
        support_trend_fig = create_yearly_support_trend(quals_df)
        if support_trend_fig:
            st.plotly_chart(support_trend_fig, use_container_width=True)
        
        # 주요 변화 지표
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 전년 대비 증가율 계산
            yearly_mean = quals_df.groupby('APPL_YEAR')[
                'APPL_SCALE_TOT_BUDGET_PRICE'
            ].mean()
            year_growth = yearly_mean.pct_change().iloc[-1]
            
            st.metric(
                "전년 대비 평균 지원금액 증가율",
                f"{year_growth:.1%}" if pd.notna(year_growth) else "정보없음"
            )
        
        with col2:
            total_programs = quals_df['BSNS_TASK_NM'].nunique()
            st.metric(
                "총 지원사업 수",
                f"{total_programs:,}개"
            )
        
        with col3:
            avg_support = quals_df['APPL_SCALE_TOT_BUDGET_PRICE'].mean()
            st.metric(
                "평균 지원금액",
                f"{avg_support:,.0f}원" if pd.notna(avg_support) else "정보없음"
            )

        # 기업 참여 트렌드
        st.header("기업 참여 트렌드")
        participation_fig = create_participation_trend(company_df)
        if participation_fig:
            st.plotly_chart(participation_fig, use_container_width=True)
        
        # 상세 통계
        st.header("상세 통계")
        
        tab1, tab2 = st.tabs(["연도별 통계", "업종별 통계"])
        
        with tab1:
            yearly_stats = quals_df.groupby('APPL_YEAR').agg({
                'BSNS_TASK_NM': 'count',
                'APPL_SCALE_TOT_BUDGET_PRICE': ['mean', 'sum']
            }).round(2)
            
            yearly_stats.columns = [
                '지원사업 수',
                '평균 지원금액',
                '총 지원금액'
            ]
            
            st.dataframe(
                yearly_stats,
                use_container_width=True
            )
        
        with tab2:
            industry_stats = company_df.groupby('INDUTY_NM').agg({
                'CMPNY_NM': 'count',
                'APPL_YEAR': ['min', 'max']
            }).round(2)
            
            industry_stats.columns = [
                '기업 수',
                '최초 참여연도',
                '최근 참여연도'
            ]
            
            st.dataframe(
                industry_stats,
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"""
            데이터 처리 중 오류가 발생했습니다.
            관리자에게 문의해주세요.
            
            오류 내용:
            {str(e)}
            
            데이터 상태:
            {quals_df.dtypes if 'quals_df' in locals() else '자격요건 데이터 로드 실패'}
            {company_df.dtypes if 'company_df' in locals() else '기업정보 데이터 로드 실패'}
        """)

if __name__ == "__main__":
    main()

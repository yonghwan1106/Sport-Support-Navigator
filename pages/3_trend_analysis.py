# 파일 위치: sports-industry-support/pages/3_trend_analysis.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys
from scipy import stats
from datetime import datetime

# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from utils import DataHandler

def create_yearly_support_trend(df):
    """연도별 지원금액 추이를 시각화합니다."""
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
        
        # 실제 데이터 추가
        fig.add_trace(
            go.Bar(
                x=yearly_stats.index,
                y=yearly_stats[('APPL_SCALE_TOT_BUDGET_PRICE', 'sum')],
                name="총 지원금액",
                marker_color='lightblue'
            ),
            secondary_y=False
        )
        
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
        
        fig.update_yaxes(title_text="총 지원금액(원)", secondary_y=False)
        fig.update_yaxes(title_text="평균 지원금액(원)", secondary_y=True)
        
        return fig
        
    except Exception as e:
        st.error(f"지원금액 추이 차트 생성 중 오류 발생: {str(e)}")
        return None

def create_participation_trend(df):
    """기업 참여 트렌드를 시각화합니다."""
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

def analyze_qualification_trends(df):
    """지원사업 자격요건의 변화 추이를 분석하고 시각화합니다."""
    try:
        # 연도별 자격요건 특성 분석
        qual_trends = df.groupby('APPL_YEAR').agg({
            'APPL_TRGET_PREPFNTN_AT': 'mean',  # 예비창업 가능 여부
            'APPL_TRGET_GRP_POSBL_AT': 'mean',  # 단체 가능 여부
            'APPL_TRGET_INDVDL_POSBL_AT': 'mean',  # 개인 가능 여부
            'STARTUP_PRIOR_AT': 'mean'  # 스타트업 우선 여부
        }).fillna(0)

        # 복합 라인 차트 생성
        fig = go.Figure()

        # 각 자격요건 추이 추가
        fig.add_trace(go.Scatter(
            x=qual_trends.index,
            y=qual_trends['APPL_TRGET_PREPFNTN_AT'] * 100,
            name='예비창업 가능',
            line=dict(color='blue')
        ))

        fig.add_trace(go.Scatter(
            x=qual_trends.index,
            y=qual_trends['APPL_TRGET_GRP_POSBL_AT'] * 100,
            name='단체 가능',
            line=dict(color='red')
        ))

        fig.add_trace(go.Scatter(
            x=qual_trends.index,
            y=qual_trends['APPL_TRGET_INDVDL_POSBL_AT'] * 100,
            name='개인 가능',
            line=dict(color='green')
        ))

        fig.add_trace(go.Scatter(
            x=qual_trends.index,
            y=qual_trends['STARTUP_PRIOR_AT'] * 100,
            name='스타트업 우선',
            line=dict(color='purple')
        ))

        fig.update_layout(
            title='자격요건 변화 추이',
            xaxis_title='연도',
            yaxis_title='비율 (%)',
            hovermode='x unified'
        )

        return fig

    except Exception as e:
        st.error(f"자격요건 트렌드 분석 중 오류 발생: {str(e)}")
        return None

def analyze_support_characteristics(df):
    """지원사업의 성격 변화를 분석하고 시각화합니다."""
    try:
        # 연도별 사업 특성 분석
        characteristics = df.groupby(['APPL_YEAR', 'APPL_REALM_NM']).size().unstack(fill_value=0)
        
        # 100% 스택 영역 차트 생성
        proportions = characteristics.div(characteristics.sum(axis=1), axis=0) * 100
        
        fig = px.area(
            proportions,
            title='지원사업 분야별 비중 변화',
            labels={'value': '비중 (%)', 'APPL_YEAR': '연도'},
            height=500
        )

        fig.update_layout(
            yaxis_title='비중 (%)',
            xaxis_title='연도',
            hovermode='x unified',
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
        st.error(f"지원사업 성격 분석 중 오류 발생: {str(e)}")
        return None

def filter_data_by_period(df, start_year, end_year):
    """지정된 기간의 데이터만 필터링합니다."""
    try:
        mask = (df['APPL_YEAR'] >= start_year) & (df['APPL_YEAR'] <= end_year)
        return df[mask]
    except Exception as e:
        st.error(f"데이터 필터링 중 오류 발생: {str(e)}")
        return df

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

    try:
        data_handler = DataHandler()
        quals_df = data_handler.get_qualification_data()
        company_df = data_handler.get_company_data()
        
        # 데이터 전처리
        for df in [quals_df, company_df]:
            if 'APPL_YEAR' in df.columns:
                df['APPL_YEAR'] = pd.to_numeric(df['APPL_YEAR'], errors='coerce')
        
        # 사이드바 - 분석 기간 설정
        st.sidebar.header("분석 기간 설정")
        min_year = int(min(quals_df['APPL_YEAR'].min(), company_df['APPL_YEAR'].min()))
        max_year = int(max(quals_df['APPL_YEAR'].max(), company_df['APPL_YEAR'].max()))
        
        selected_years = st.sidebar.slider(
            "분석 기간 선택",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )
        
        # 선택된 기간으로 데이터 필터링
        quals_df = filter_data_by_period(quals_df, selected_years[0], selected_years[1])
        company_df = filter_data_by_period(company_df, selected_years[0], selected_years[1])
        
        # 트렌드 분석 섹션
        st.header("지원사업 트렌드")
        support_trend_fig = create_yearly_support_trend(quals_df)
        if support_trend_fig:
            st.plotly_chart(support_trend_fig, use_container_width=True)
        
        # 주요 변화 지표
        col1, col2, col3 = st.columns(3)
        
        with col1:
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

        # 자격요건 변화 분석
        st.header("자격요건 변화 분석")
        qual_trend_fig = analyze_qualification_trends(quals_df)
        if qual_trend_fig:
            st.plotly_chart(qual_trend_fig, use_container_width=True)
            
            # 자격요건 변화에 대한 인사이트
            st.markdown("### 주요 인사이트")
            latest_year = quals_df['APPL_YEAR'].max()
            early_year = quals_df['APPL_YEAR'].min()
            
            # 예비창업 가능 비율 변화
            early_prep = quals_df[quals_df['APPL_YEAR']==early_year]['APPL_TRGET_PREPFNTN_AT'].mean()
            latest_prep = quals_df[quals_df['APPL_YEAR']==latest_year]['APPL_TRGET_PREPFNTN_AT'].mean()
            prep_change = (latest_prep - early_prep) * 100
            
            st.write(f"예비창업자 지원 가능 비율이 {abs(prep_change):.1f}% {'증가' if prep_change > 0 else '감소'}했습니다.")

        # 지원사업 성격 변화 분석
        st.header("지원사업 성격 변화")
        char_trend_fig = analyze_support_characteristics(quals_df)
        if char_trend_fig:
            st.plotly_chart(char_trend_fig, use_container_width=True)
            
            # 지원분야 다양성 분석
            st.markdown("### 지원분야 다양성 분석")
            yearly_diversity = quals_df.groupby('APPL_YEAR')['APPL_REALM_NM'].nunique()
            diversity_change = yearly_diversity.iloc[-1] - yearly_diversity.iloc[0]
            
            st.write(f"{early_year}년 대비 {latest_year}년의 지원분야가 {abs(diversity_change)}개 {'증가' if diversity_change > 0 else '감소'}했습니다.")

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
            
            st.dataframe(yearly_stats, use_container_width=True)

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
           
           st.dataframe(industry_stats, use_container_width=True)

       # 트렌드 변화 요약
       st.header("트렌드 분석 요약")
       st.markdown("""
           ### 주요 변화 포인트

           1. **자격요건 변화**
           - 예비창업자 지원 가능성이 확대되는 추세
           - 개인/단체 참여 조건이 점차 유연화
           - 스타트업 우선지원 정책 강화

           2. **지원 규모 변화**
           - 전체 지원금액은 증가 추세
           - 사업당 평균 지원금액도 상승
           - 지원사업의 수와 다양성이 확대

           3. **산업 분야별 특성**
           - 다양한 업종으로 지원 범위 확대
           - 신규 참여 업종의 지속적 증가
           - 특정 분야 집중 지원 정책 확인

           4. **미래 전망**
           - 스타트업 생태계 활성화 정책 지속 예상
           - 지원 규모의 지속적 확대 전망
           - 지원 대상과 방식의 다변화 예상
       """)

       # 시사점 및 제언
       st.markdown("""
           ### 시사점 및 제언
           
           1. **정책적 시사점**
           - 스포츠산업의 창업 생태계가 지속적으로 확대
           - 다양한 형태의 사업자 참여 기회 증가
           - 지원 정책의 포용성과 효과성 개선
           
           2. **기업을 위한 제언**
           - 자격요건 변화 트렌드를 고려한 사업 계획 수립
           - 지원사업 특성에 맞는 맞춤형 준비 필요
           - 장기적 관점의 지원사업 활용 전략 수립
           
           3. **향후 고려사항**
           - 신규 진입 업종에 대한 지원체계 보완
           - 성과 분석을 통한 지원 효과성 제고
           - 산업 환경 변화에 대응하는 유연한 지원체계 구축
       """)
           
   except Exception as e:
       st.error(f"""
           데이터 처리 중 오류가 발생했습니다.
           관리자에게 문의해주세요.
           
           오류 내용:
           {str(e)}
       """)

if __name__ == "__main__":
   main()
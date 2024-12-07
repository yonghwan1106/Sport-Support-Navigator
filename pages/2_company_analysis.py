# 파일 위치: sports-industry-support/pages/2_company_analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import requests
import sys

# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from utils import DataHandler

def create_korea_choropleth(df):
    """
    대한민국 지도 기반의 기업 분포 시각화를 생성합니다.
    """
    # 시도별 위도/경도 좌표 (중심점)
    korea_coordinates = {
        '서울': {'lat': 37.5665, 'lon': 126.9780},
        '부산': {'lat': 35.1796, 'lon': 129.0756},
        '대구': {'lat': 35.8714, 'lon': 128.6014},
        '인천': {'lat': 37.4563, 'lon': 126.7052},
        '광주': {'lat': 35.1595, 'lon': 126.8526},
        '대전': {'lat': 36.3504, 'lon': 127.3845},
        '울산': {'lat': 35.5384, 'lon': 129.3114},
        '세종': {'lat': 36.4800, 'lon': 127.2890},
        '경기': {'lat': 37.4138, 'lon': 127.5183},
        '강원': {'lat': 37.8228, 'lon': 128.1555},
        '충북': {'lat': 36.6358, 'lon': 127.4914},
        '충남': {'lat': 36.6588, 'lon': 126.6728},
        '전북': {'lat': 35.8202, 'lon': 127.1088},
        '전남': {'lat': 34.8160, 'lon': 126.4631},
        '경북': {'lat': 36.4919, 'lon': 128.8889},
        '경남': {'lat': 35.4606, 'lon': 128.2132},
        '제주': {'lat': 33.4890, 'lon': 126.4983}
    }

    # 지역별 기업 수 계산
    region_counts = df['지역'].value_counts()

    # 지도 생성
    fig = go.Figure()

    # 지역별 마커 추가
    for region, count in region_counts.items():
        if region in korea_coordinates:
            coord = korea_coordinates[region]
            
            fig.add_trace(go.Scattergeo(
                lon=[coord['lon']],
                lat=[coord['lat']],
                text=f'{region}: {count}개 기업',
                mode='markers+text',
                marker=dict(
                    size=count/5 + 10,  # 기업 수에 비례한 마커 크기
                    color='red',
                    opacity=0.7
                ),
                name=region
            ))

    # 지도 레이아웃 설정
    fig.update_layout(
        title='지역별 기업 분포',
        geo=dict(
            scope='asia',
            center=dict(lon=127.5, lat=36),
            projection_scale=20,
            showland=True,
            showcountries=True,
            countrycolor='lightgray',
            showsubunits=True,
            subunitcolor='lightblue'
        )
    )

    return fig

def create_industry_drilldown(df):
    """
    업종별 드릴다운 차트를 생성합니다.
    """
    # 대분류 업종
    main_categories = df['INDUTY_NM'].str.split().str[0].value_counts()
    
    # 전체 업종
    all_categories = df['INDUTY_NM'].value_counts()
    
    # 대분류별 하위 업종 집계
    subcategories = {}
    for main_cat in main_categories.index:
        mask = df['INDUTY_NM'].str.startswith(main_cat)
        subcategories[main_cat] = df[mask]['INDUTY_NM'].value_counts()

    # 드릴다운 차트 생성
    fig = go.Figure()
    
    # 대분류 바 차트
    fig.add_trace(go.Bar(
        x=main_categories.index,
        y=main_categories.values,
        name='대분류',
        marker_color='lightblue'
    ))
    
    # 하위 분류 바 차트 (초기에는 숨김)
    for main_cat, subcat_data in subcategories.items():
        fig.add_trace(go.Bar(
            x=subcat_data.index,
            y=subcat_data.values,
            name=main_cat,
            visible=False
        ))

    # 버튼 생성
    updatemenus = [
        dict(
            buttons=list([
                dict(
                    args=[{"visible": [True] + [False]*len(subcategories)}],
                    label="대분류",
                    method="update"
                )
            ] + [
                dict(
                    args=[{
                        "visible": [i == idx + 1 for i in range(len(subcategories) + 1)]
                    }],
                    label=main_cat,
                    method="update"
                )
                for idx, main_cat in enumerate(subcategories.keys())
            ]),
            direction="down",
            showactive=True,
            x=0.1,
            y=1.15
        )
    ]

    fig.update_layout(
        title="업종별 기업 분포 (드릴다운)",
        updatemenus=updatemenus,
        showlegend=False
    )

    return fig

def fetch_company_news(company_name):
    """
    기업 관련 뉴스를 가져옵니다.
    실제 구현 시에는 적절한 뉴스 API를 사용해야 합니다.
    """
    try:
        # 예시 데이터 반환 (실제 구현 시 API 호출로 대체)
        return [
            {
                'title': f'{company_name} 관련 샘플 뉴스 1',
                'date': '2024-01-07',
                'summary': '뉴스 내용 요약...'
            },
            {
                'title': f'{company_name} 관련 샘플 뉴스 2',
                'date': '2024-01-06',
                'summary': '뉴스 내용 요약...'
            }
        ]
    except Exception:
        return []

def main():
    st.set_page_config(
        page_title="기업 분석",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 지원기업 특성 분석")
    st.markdown("이 페이지에서는 스포츠산업 지원사업에 참여한 기업들의 특성을 분석합니다.")

    try:
        data_handler = DataHandler()
        company_df = data_handler.get_company_data()

        # 사이드바 필터
        with st.sidebar:
            st.header("분석 필터")
            
            years = sorted(company_df['APPL_YEAR'].unique(), reverse=True)
            selected_year = st.selectbox(
                "분석 년도",
                options=years
            )
            
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

        # 주요 지표
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
                f"{avg_age:.1f}년"
            )
        
        with col3:
            unique_regions = filtered_df['지역'].nunique()
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

        # 분석 탭 구성
        tab1, tab2, tab3, tab4 = st.tabs([
            "지역 분포",
            "업종 분석",
            "상세 정보",
            "뉴스 및 공시"
        ])
        
        with tab1:
            st.subheader("지역별 기업 분포")
            map_fig = create_korea_choropleth(filtered_df)
            st.plotly_chart(map_fig, use_container_width=True)
            
            # 추가 지역 통계
            st.subheader("지역별 상세 통계")
            region_stats = filtered_df.groupby('지역').agg({
                'CMPNY_NM': 'count',
                '업력': 'mean'
            }).round(2)
            region_stats.columns = ['기업 수', '평균 업력']
            st.dataframe(
                region_stats.sort_values('기업 수', ascending=False),
                use_container_width=True
            )
        
        with tab2:
            st.subheader("업종별 분석")
            drilldown_fig = create_industry_drilldown(filtered_df)
            st.plotly_chart(drilldown_fig, use_container_width=True)
            
            # 업종별 추가 분석
            st.subheader("업종별 평균 업력")
            industry_age = filtered_df.groupby('INDUTY_NM')['업력'].mean()
            
            fig = px.bar(
                x=industry_age.index,
                y=industry_age.values,
                labels={'x': '업종', 'y': '평균 업력(년)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("기업 상세 정보")
            
            # 검색 필터
            search_term = st.text_input("기업명 검색")
            
            if search_term:
                display_df = filtered_df[
                    filtered_df['CMPNY_NM'].str.contains(search_term, na=False)
                ]
            else:
                display_df = filtered_df
            
            display_columns = [
                'CMPNY_NM', 'RPRSNTV_NM', 'INDUTY_NM',
                'CMPNY_ADDR', 'BSNS_NO', 'APPL_YEAR'
            ]
            
            column_mapping = {
                'CMPNY_NM': '기업명',
                'RPRSNTV_NM': '대표자명',
                'INDUTY_NM': '업종',
                'CMPNY_ADDR': '주소',
                'BSNS_NO': '사업자번호',
                'APPL_YEAR': '지원년도'
            }
            
            display_df = display_df[display_columns].rename(columns=column_mapping)
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
        
        with tab4:
            st.subheader("기업 뉴스 및 공시 정보")
            
            # 기업 선택
            selected_company = st.selectbox(
                "기업 선택",
                options=filtered_df['CMPNY_NM'].unique()
            )
            
            if selected_company:
                # 뉴스 정보 표시
                st.markdown("### 관련 뉴스")
                news_items = fetch_company_news(selected_company)
                
                if news_items:
                    for news in news_items:
                        with st.expander(f"{news['date']} - {news['title']}"):
                            st.write(news['summary'])
                else:
                    st.info("관련 뉴스가 없습니다.")
                
                # 기업 기본 정보 표시
                st.markdown("### 기업 정보")
                company_info = filtered_df[
                    filtered_df['CMPNY_NM'] == selected_company
                ].iloc[0]
                
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.write(f"**업종:** {company_info['INDUTY_NM']}")
                    st.write(f"**대표자:** {company_info['RPRSNTV_NM']}")
                
                with info_col2:
                    st.write(f"**소재지:** {company_info['CMPNY_ADDR']}")
                    st.write(f"**지원년도:** {company_info['APPL_YEAR']}")
            
    except Exception as e:
        st.error(f"""
            데이터 처리 중 오류가 발생했습니다.
            관리자에게 문의해주세요.
            
            오류 내용:
            {str(e)}
        """)

if __name__ == "__main__":
    main()

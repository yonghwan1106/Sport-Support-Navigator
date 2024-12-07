# 파일 위치: sports-industry-support/pages/1_program_search.py

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import json
import base64
import io
from datetime import datetime
import sys

# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from utils import DataHandler

def save_search_conditions(conditions, name):
    """검색 조건을 세션 스테이트에 저장합니다."""
    if 'saved_conditions' not in st.session_state:
        st.session_state.saved_conditions = {}
    
    st.session_state.saved_conditions[name] = conditions
    st.success(f'검색 조건 "{name}"이(가) 저장되었습니다.')

def load_search_conditions(name):
    """저장된 검색 조건을 불러옵니다."""
    if name in st.session_state.saved_conditions:
        return st.session_state.saved_conditions[name]
    return None

def convert_df_to_excel(df):
    """
    데이터프레임을 Excel 파일로 변환합니다.
    XlsxWriter 패키지가 없는 경우 openpyxl을 사용합니다.
    """
    try:
        output = io.BytesIO()
        
        try:
            # XlsxWriter를 사용한 변환 시도
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='검색결과', index=False)
                
                # 워크시트와 워크북 객체 가져오기
                workbook = writer.book
                worksheet = writer.sheets['검색결과']
                
                # 열 너비 자동 조정
                for i, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).str.len().max(),
                        len(col)
                    )
                    worksheet.set_column(i, i, max_length + 2)
                    
        except (ImportError, ModuleNotFoundError):
            # openpyxl을 사용한 대체 변환
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='검색결과', index=False)
        
        return output.getvalue()
        
    except Exception as e:
        st.error(f"""
            Excel 파일 생성 중 오류가 발생했습니다.
            CSV 형식으로 다운로드해 주세요.
            
            오류 내용:
            {str(e)}
        """)
        return None

def convert_df_to_pdf(df):
    """데이터프레임을 PDF로 변환합니다."""
    # PDF 변환 로직 구현
    # (실제 구현 시에는 reportlab 또는 다른 PDF 라이브러리 사용)
    pass

def format_amount(amount):
    """금액을 읽기 쉬운 한국어 형식으로 변환합니다."""
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
    st.set_page_config(
        page_title="지원사업 자격요건 검색",
        layout="wide"
    )
    
    st.title("💡 지원사업 자격요건 검색")
    st.markdown("기업 조건에 맞는 지원사업을 찾아보세요.")
    
    try:
        # 데이터 핸들러 초기화
        data_handler = DataHandler()
        
        # 사이드바에 검색 필터 구성
        with st.sidebar:
            st.header("검색 필터")
            
            # 필터 상단에 저장된 조건 불러오기 옵션 추가
            if 'saved_conditions' in st.session_state and st.session_state.saved_conditions:
                selected_condition = st.selectbox(
                    "저장된 검색 조건",
                    ['새로 검색'] + list(st.session_state.saved_conditions.keys())
                )
                
                if selected_condition != '새로 검색':
                    saved_condition = load_search_conditions(selected_condition)
                    if saved_condition:
                        st.success(f'"{selected_condition}" 조건을 불러왔습니다.')
            
            # 검색 조건 입력 폼
            with st.form("search_form"):
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
                
                # 검색 실행 버튼
                submitted = st.form_submit_button("검색")
                
                if submitted:
                    # 현재 검색 조건 저장
                    st.session_state.current_conditions = {
                        'year': selected_year,
                        'categories': selected_categories,
                        'company_age': company_age,
                        'is_startup': is_startup,
                        'support_amount': support_amount
                    }
            
            # 검색 조건 저장 섹션
            if 'current_conditions' in st.session_state:
                st.divider()
                st.subheader("검색 조건 저장")
                condition_name = st.text_input("저장할 이름")
                if st.button("현재 조건 저장"):
                    if condition_name:
                        save_search_conditions(
                            st.session_state.current_conditions,
                            condition_name
                        )
                    else:
                        st.warning("저장할 이름을 입력해주세요.")

        # 메인 영역 구성
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 검색 결과 표시
            st.subheader("검색 결과")
            
            # 데이터 필터링
            if 'current_conditions' in st.session_state:
                conditions = st.session_state.current_conditions
                filtered_df = data_handler.filter_qualifications(
                    year=conditions['year'],
                    categories=conditions['categories'],
                    company_age=conditions['company_age'],
                    is_startup=conditions['is_startup'],
                    min_amount=conditions['support_amount'][0]*100000000,
                    max_amount=conditions['support_amount'][1]*100000000
                )
                
                if len(filtered_df) == 0:
                    st.warning("검색 조건에 맞는 지원사업이 없습니다.")
                else:
                    # 결과 표시 및 다운로드 옵션
                    display_cols = [
                        'BSNS_TASK_NM',
                        'APPL_YEAR',
                        'RCRIT_PD_BEGIN_DE',
                        'RCRIT_PD_END_DE',
                        'APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE'
                    ]
                    
                    # 날짜 형식 변환
                    for col in ['RCRIT_PD_BEGIN_DE', 'RCRIT_PD_END_DE']:
                        filtered_df[col] = pd.to_datetime(
                            filtered_df[col]
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
                    
                    # 결과 표시
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # 다운로드 옵션
                    st.divider()
                    download_col1, download_col2 = st.columns(2)
                    
                    with download_col1:
                        # 엑셀 다운로드
                        excel_data = convert_df_to_excel(display_df)
                        st.download_button(
                            label="Excel 파일로 다운로드",
                            data=excel_data,
                            file_name=f'지원사업검색결과_{datetime.now().strftime("%Y%m%d")}.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                    
                    with download_col2:
                        # CSV 다운로드
                        csv_data = display_df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="CSV 파일로 다운로드",
                            data=csv_data,
                            file_name=f'지원사업검색결과_{datetime.now().strftime("%Y%m%d")}.csv',
                            mime='text/csv'
                        )
        
        with col2:
            # 통계 및 시각화
            if 'current_conditions' in st.session_state and len(filtered_df) > 0:
                st.subheader("지원사업 통계")
                
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
            
    except Exception as e:
        st.error(f"""
            데이터 처리 중 오류가 발생했습니다.
            관리자에게 문의해주세요.
            
            오류 내용:
            {str(e)}
        """)

if __name__ == "__main__":
    main()

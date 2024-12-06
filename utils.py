# 파일 위치: sports-industry-support/utils.py
#
# 이 파일은 데이터 처리를 위한 핵심 유틸리티 클래스들을 포함하고 있습니다.
# 모든 페이지에서 공통적으로 사용되는 데이터 처리 기능을 제공합니다.

import os  # 운영체제 관련 기능을 사용하기 위한 모듈
from pathlib import Path  # 파일 경로 처리를 위한 모듈
import streamlit as st  # 웹 애플리케이션 구현을 위한 라이브러리
import pandas as pd  # 데이터 처리를 위한 라이브러리

class DataPathHandler:
    """
    데이터 파일 경로를 관리하는 클래스입니다.
    로컬 개발 환경과 배포 환경 모두에서 올바르게 작동하도록 설계되었습니다.
    """
    
    def __init__(self):
        """
        DataPathHandler를 초기화합니다.
        실행 환경을 감지하여 적절한 기본 경로를 설정합니다.
        """
        # Streamlit Cloud 환경인지 확인
        if os.getenv('STREAMLIT_CLOUD'):
            # Streamlit Cloud에서 실행 중일 때
            self.base_path = Path.cwd() / 'data'
        else:
            # 로컬 환경에서 실행 중일 때
            current_file = Path(__file__).resolve()  # 현재 파일의 절대 경로
            self.base_path = current_file.parent / 'data'  # data 디렉토리 경로
            
        # data 디렉토리가 존재하는지 확인
        if not self.base_path.exists():
            raise FileNotFoundError(
                f"데이터 디렉토리를 찾을 수 없습니다: {self.base_path}"
            )

    @st.cache_data  # 데이터 캐싱으로 성능 향상
    def load_csv(self, filename: str) -> pd.DataFrame:
        """
        CSV 파일을 데이터프레임으로 읽어옵니다.
        
        매개변수:
            filename (str): 읽어올 CSV 파일의 이름
            
        반환값:
            pandas.DataFrame: CSV 파일의 내용을 담은 데이터프레임
            
        예외:
            FileNotFoundError: 파일을 찾을 수 없을 때 발생
        """
        # 전체 파일 경로 생성
        file_path = self.base_path / filename
        
        # 파일 존재 여부 확인
        if not file_path.exists():
            raise FileNotFoundError(
                f"데이터 파일을 찾을 수 없습니다: {filename}\n"
                f"확인한 경로: {file_path}"
            )
            
        try:
            # UTF-8 인코딩으로 먼저 시도
            try:
                df = pd.read_csv(file_path)
            except UnicodeDecodeError:
                # UTF-8로 읽기 실패시 cp949(한글 인코딩)로 시도
                df = pd.read_csv(file_path, encoding='cp949')
                
            return df
            
        except Exception as e:
            st.error(f"{filename} 파일 로딩 중 오류 발생: {str(e)}")
            raise

class DataHandler:
    """
    데이터 처리를 위한 메인 클래스입니다.
    데이터 로딩, 전처리, 분석 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        """
        DataHandler를 초기화하고 필요한 데이터를 로드합니다.
        """
        # 경로 관리자 초기화
        self.path_handler = DataPathHandler()
        # 데이터 로드
        self.load_data()
        # 데이터 전처리 수행
        self.preprocess_data()
    
    def load_data(self):
        """
        필요한 모든 데이터 파일을 로드합니다.
        오류 발생시 사용자에게 알림을 표시합니다.
        """
        try:
            # 지원사업 자격요건 데이터 로드
            self.qualifications_df = self.path_handler.load_csv(
                'program_qualifications.csv'
            )
            self.qual_columns = self.path_handler.load_csv(
                'program_qualifications_columns.csv'
            )
            
            # 기업정보 데이터 로드
            self.company_df = self.path_handler.load_csv(
                'company_info.csv'
            )
            self.company_columns = self.path_handler.load_csv(
                'company_info_columns.csv'
            )
            
        except FileNotFoundError as e:
            st.error(f"데이터 로딩 오류: {str(e)}")
            raise
        except Exception as e:
            st.error(f"예상치 못한 오류 발생: {str(e)}")
            raise

    def preprocess_data(self):
        """
        로드된 데이터에 대한 전처리를 수행합니다.
        날짜 형식 변환, 금액 데이터 정리 등을 수행합니다.
        """
        # 날짜 컬럼 전처리
        date_columns = ['RCRIT_PD_BEGIN_DE', 'RCRIT_PD_END_DE']
        for col in date_columns:
            if col in self.qualifications_df.columns:
                self.qualifications_df[col] = pd.to_datetime(
                    self.qualifications_df[col],
                    format='%Y%m%d',
                    errors='coerce'  # 오류 발생시 NaT로 처리
                )
        
        # 금액 컬럼 전처리
        amount_columns = [
            'APPL_SCALE_TOT_BUDGET_PRICE',
            'APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE'
        ]
        for col in amount_columns:
            if col in self.qualifications_df.columns:
                # 쉼표 제거 후 숫자로 변환
                self.qualifications_df[col] = pd.to_numeric(
                    self.qualifications_df[col].astype(str).str.replace(',', ''),
                    errors='coerce'  # 오류 발생시 NaN으로 처리
                )
        
        # 기업정보 전처리
        if 'BSNS_NO' in self.company_df.columns:
            # 사업자등록번호에서 설립연도 추출 (앞 4자리)
            self.company_df['설립연도'] = self.company_df['BSNS_NO'].str[:4]
            # 현재 년도 기준 업력 계산
            current_year = 2024
            self.company_df['업력'] = current_year - \
                pd.to_numeric(self.company_df['설립연도'], errors='coerce')

    def get_qualification_data(self) -> pd.DataFrame:
        """자격요건 데이터를 반환합니다."""
        return self.qualifications_df
    
    def get_company_data(self) -> pd.DataFrame:
        """기업정보 데이터를 반환합니다."""
        return self.company_df

    # 여기에 필요한 추가 메소드들을 구현할 수 있습니다.

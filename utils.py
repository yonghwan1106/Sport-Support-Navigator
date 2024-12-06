# 파일 위치: sports-industry-support/utils.py

import os
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

class DataPathHandler:
    """데이터 파일 경로를 관리하는 클래스입니다."""
    
    def __init__(self):
        # Streamlit Cloud 환경인지 확인하여 적절한 경로 설정
        if os.getenv('STREAMLIT_CLOUD'):
            self.base_path = Path.cwd() / 'data'
        else:
            current_file = Path(__file__).resolve()
            self.base_path = current_file.parent / 'data'
            
        if not self.base_path.exists():
            raise FileNotFoundError(
                f"데이터 디렉토리를 찾을 수 없습니다: {self.base_path}"
            )

    @st.cache_data
    def load_csv(_self, filename: str) -> pd.DataFrame:
        """CSV 파일을 데이터프레임으로 읽어옵니다."""
        file_path = _self.base_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"데이터 파일을 찾을 수 없습니다: {filename}\n"
                f"확인한 경로: {file_path}"
            )
            
        try:
            try:
                df = pd.read_csv(file_path)
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='cp949')
                
            return df
            
        except Exception as e:
            st.error(f"{filename} 파일 로딩 중 오류 발생: {str(e)}")
            raise

class DataHandler:
    """데이터 처리를 위한 메인 클래스입니다."""
    
    def __init__(self):
        """DataHandler를 초기화하고 필요한 데이터를 로드합니다."""
        self.path_handler = DataPathHandler()
        self.load_data()
        self.preprocess_data()
    
    def load_data(self):
        """필요한 모든 데이터 파일을 로드합니다."""
        try:
            self.qualifications_df = self.path_handler.load_csv(
                'program_qualifications.csv'
            )
            self.qual_columns = self.path_handler.load_csv(
                'program_qualifications_columns.csv'
            )
            
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

    def safe_string_operation(self, series):
        """문자열 작업을 안전하게 수행하는 헬퍼 함수입니다."""
        # None, NA 값을 빈 문자열로 변환
        series = series.fillna('')
        # 모든 값을 문자열로 변환
        return series.astype(str)

    def extract_region(self, address):
        """주소에서 지역명을 안전하게 추출하는 함수입니다."""
        try:
            if pd.isna(address) or not isinstance(address, str):
                return ''
            parts = address.strip().split()
            return parts[0] if parts else ''
        except Exception:
            return ''

    def preprocess_data(self):
        """데이터 전처리를 수행합니다."""
        try:
            # 회사 데이터 전처리
            if 'CMPNY_ADDR' in self.company_df.columns:
                # 주소 데이터를 안전하게 문자열로 변환
                self.company_df['CMPNY_ADDR'] = self.safe_string_operation(
                    self.company_df['CMPNY_ADDR']
                )
                
                # 지역 정보 추출
                self.company_df['지역'] = self.company_df['CMPNY_ADDR'].apply(
                    self.extract_region
                )

            # 사업자등록번호 처리
            if 'BSNS_NO' in self.company_df.columns:
                self.company_df['BSNS_NO'] = self.safe_string_operation(
                    self.company_df['BSNS_NO']
                )
                
                # 설립연도 추출 (앞 4자리)
                self.company_df['설립연도'] = self.company_df['BSNS_NO'].str[:4]
                # 숫자가 아닌 경우 NaN으로 변환
                self.company_df['설립연도'] = pd.to_numeric(
                    self.company_df['설립연도'], 
                    errors='coerce'
                )
                
                # 업력 계산
                current_year = 2024
                self.company_df['업력'] = current_year - self.company_df['설립연도']
                
                # 비정상적인 업력 처리 (음수나 너무 큰 값)
                mask = (self.company_df['업력'] < 0) | (self.company_df['업력'] > 100)
                self.company_df.loc[mask, '업력'] = np.nan

            # 자격요건 데이터 전처리
            date_columns = ['RCRIT_PD_BEGIN_DE', 'RCRIT_PD_END_DE']
            for col in date_columns:
                if col in self.qualifications_df.columns:
                    # 날짜 형식으로 변환
                    self.qualifications_df[col] = pd.to_datetime(
                        self.qualifications_df[col],
                        format='%Y%m%d',
                        errors='coerce'
                    )

            # 금액 데이터 전처리
            amount_columns = [
                'APPL_SCALE_TOT_BUDGET_PRICE',
                'APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE'
            ]
            for col in amount_columns:
                if col in self.qualifications_df.columns:
                    # 쉼표 제거 후 숫자로 변환
                    self.qualifications_df[col] = pd.to_numeric(
                        self.qualifications_df[col].astype(str).str.replace(',', ''),
                        errors='coerce'
                    )

        except Exception as e:
            st.error(f"데이터 전처리 중 오류 발생: {str(e)}")
            # 오류 발생 시에도 기본적인 동작이 가능하도록 함
            pass

    def get_qualification_data(self) -> pd.DataFrame:
        """자격요건 데이터를 반환합니다."""
        return self.qualifications_df
    
    def get_company_data(self) -> pd.DataFrame:
        """기업정보 데이터를 반환합니다."""
        return self.company_df

    def get_available_years(self) -> list:
        """사용 가능한 연도 목록을 반환합니다."""
        return sorted(self.qualifications_df['APPL_YEAR'].unique().tolist())

    def get_support_categories(self) -> list:
        """지원 분야 목록을 반환합니다."""
        return sorted(self.qualifications_df['APPL_REALM_NM'].unique().tolist())

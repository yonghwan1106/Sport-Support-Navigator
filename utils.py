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

# 파일 위치: sports-industry-support/utils.py
# DataHandler 클래스에 다음 메서드를 추가하세요

    def filter_qualifications(
        self, 
        year=None, 
        categories=None, 
        company_age=None,
        is_startup=False,
        min_amount=None,
        max_amount=None
    ):
        """
        지원사업 데이터를 주어진 조건에 따라 필터링합니다.
        
        매개변수:
            year (int): 지원년도
            categories (list): 지원분야 목록
            company_age (int): 기업 업력
            is_startup (bool): 예비창업자 여부
            min_amount (float): 최소 지원금액
            max_amount (float): 최대 지원금액
        
        반환값:
            DataFrame: 필터링된 지원사업 데이터
        """
        try:
            # 기본 데이터 복사
            filtered_df = self.qualifications_df.copy()
            
            # 연도 필터링
            if year is not None:
                filtered_df = filtered_df[filtered_df['APPL_YEAR'] == year]
            
            # 지원분야 필터링
            if categories and len(categories) > 0:
                filtered_df = filtered_df[
                    filtered_df['APPL_REALM_NM'].isin(categories)
                ]
            
            # 예비창업자 여부에 따른 필터링
            if is_startup:
                filtered_df = filtered_df[
                    filtered_df['APPL_TRGET_PREPFNTN_AT'] == 'Y'
                ]
            
            # 기업 업력 조건 필터링
            if company_age is not None:
                # 업력 관련 컬럼이 있는 경우에만 처리
                if 'APPL_TRGET_RM_CN' in filtered_df.columns:
                    # 예: "3년 이상" 같은 텍스트에서 숫자 추출
                    filtered_df = filtered_df[
                        filtered_df['APPL_TRGET_RM_CN'].str.contains(
                            str(company_age),
                            na=False
                        )
                    ]
            
            # 지원금액 범위 필터링
            amount_col = 'APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE'
            if min_amount is not None:
                filtered_df = filtered_df[
                    filtered_df[amount_col] >= min_amount
                ]
            if max_amount is not None:
                filtered_df = filtered_df[
                    filtered_df[amount_col] <= max_amount
                ]
            
            return filtered_df
            
        except Exception as e:
            st.error(f"데이터 필터링 중 오류 발생: {str(e)}")
            return pd.DataFrame()  # 빈 데이터프레임 반환
        
    # 파일 위치: sports-industry-support/utils.py의 DataHandler 클래스에 추가

    def parse_company_age_condition(self, condition_text):
        """
        기업 업력 조건 텍스트를 파싱하여 최소, 최대 업력을 추출합니다.
        
        매개변수:
            condition_text (str): 업력 조건이 포함된 텍스트
            
        반환값:
            tuple: (최소업력, 최대업력) 형태의 튜플
        """
        try:
            if pd.isna(condition_text):
                return (None, None)
                
            text = str(condition_text).replace(" ", "")
            
            # 예비창업자 조건 처리
            if "예비창업자" in text:
                return (0, 0)
                
            # 숫자 추출
            import re
            numbers = re.findall(r'\d+', text)
            numbers = [int(n) for n in numbers]
            
            if not numbers:
                return (None, None)
                
            if len(numbers) == 1:
                # "N년 미만" 형태
                if "미만" in text:
                    return (0, numbers[0])
                # "N년 이상" 형태
                if "이상" in text:
                    return (numbers[0], None)
                return (None, None)
                
            if len(numbers) == 2:
                # "N년 이상 ~ M년 미만" 형태
                return (numbers[0], numbers[1])
                
            return (None, None)
            
        except Exception:
            return (None, None)

    def check_company_age_condition(self, condition_text, target_age):
        """
        주어진 업력이 조건을 만족하는지 확인합니다.
        
        매개변수:
            condition_text (str): 업력 조건이 포함된 텍스트
            target_age (int): 확인할 기업 업력
            
        반환값:
            bool: 조건 만족 여부
        """
        min_age, max_age = self.parse_company_age_condition(condition_text)
        
        if min_age is None and max_age is None:
            return True
            
        if min_age is not None and target_age < min_age:
            return False
            
        if max_age is not None and target_age >= max_age:
            return False
            
        return True

    def normalize_amount(self, amount_str):
        """
        금액 문자열을 숫자로 정규화합니다.
        
        매개변수:
            amount_str: 금액 문자열 또는 숫자
            
        반환값:
            float: 정규화된 금액
        """
        try:
            if pd.isna(amount_str):
                return None
                
            if isinstance(amount_str, (int, float)):
                return float(amount_str)
                
            # 문자열에서 숫자만 추출
            import re
            numbers = re.findall(r'[\d.]+', str(amount_str))
            if not numbers:
                return None
                
            amount = float(numbers[0])
            
            # 단위 변환
            if "억원" in str(amount_str):
                amount *= 100000000
            elif "만원" in str(amount_str):
                amount *= 10000
                
            return amount
            
        except Exception:
            return None

    def filter_qualifications(
        self, 
        year=None, 
        categories=None, 
        company_age=None,
        is_startup=False,
        min_amount=None,
        max_amount=None
    ):
        """
        지원사업 데이터를 주어진 조건에 따라 필터링합니다.
        
        매개변수는 이전과 동일
        """
        try:
            # 기본 데이터 복사
            filtered_df = self.qualifications_df.copy()
            
            # 연도 필터링
            if year is not None:
                filtered_df = filtered_df[filtered_df['APPL_YEAR'] == year]
            
            # 지원분야 필터링
            if categories and len(categories) > 0:
                filtered_df = filtered_df[
                    filtered_df['APPL_REALM_NM'].isin(categories)
                ]
            
            # 예비창업자 여부에 따른 필터링
            if is_startup:
                filtered_df = filtered_df[
                    filtered_df['APPL_TRGET_PREPFNTN_AT'] == 'Y'
                ]
            
            # 기업 업력 조건 필터링
            if company_age is not None:
                filtered_df = filtered_df[
                    filtered_df['APPL_TRGET_RM_CN'].apply(
                        lambda x: self.check_company_age_condition(x, company_age)
                    )
                ]
            
            # 지원금액 범위 필터링
            filtered_df['정규화금액'] = filtered_df['APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE'].apply(
                self.normalize_amount
            )
            
            if min_amount is not None:
                filtered_df = filtered_df[
                    (filtered_df['정규화금액'].isna()) | 
                    (filtered_df['정규화금액'] >= min_amount)
                ]
                
            if max_amount is not None:
                filtered_df = filtered_df[
                    (filtered_df['정규화금액'].isna()) | 
                    (filtered_df['정규화금액'] <= max_amount)
                ]
            
            # 임시 컬럼 제거
            filtered_df = filtered_df.drop('정규화금액', axis=1)
            
            return filtered_df
            
        except Exception as e:
            st.error(f"데이터 필터링 중 오류 발생: {str(e)}")
            return pd.DataFrame()  # 빈 데이터프레임 반환

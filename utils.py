# utils.py

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Union

class DataHandler:
    """데이터 처리를 위한 핵심 클래스입니다.
    모든 페이지에서 공통적으로 사용되는 데이터 처리 기능을 제공합니다.
    """
    
    def __init__(self, data_path: Path):
        """데이터 핸들러를 초기화합니다.
        
        Args:
            data_path (Path): 데이터 파일들이 저장된 디렉토리 경로
        """
        self.data_path = data_path
        self.load_data()
        self.preprocess_data()
        
    def load_data(self):
        """데이터 파일들을 로드하고 기본적인 전처리를 수행합니다."""
        try:
            # 자격요건 데이터 로드
            self.qualifications_df = pd.read_csv(
                self.data_path / 'program_qualifications.csv'
            )
            self.qual_columns = pd.read_csv(
                self.data_path / 'program_qualifications_columns.csv'
            )
            
            # 기업정보 데이터 로드
            self.company_df = pd.read_csv(
                self.data_path / 'company_info.csv'
            )
            self.company_columns = pd.read_csv(
                self.data_path / 'company_info_columns.csv'
            )
            
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"필요한 데이터 파일을 찾을 수 없습니다: {e}"
            )
            
    def preprocess_data(self):
        """데이터 전처리를 수행합니다.
        
        날짜, 금액 등의 데이터 타입을 변환하고,
        필요한 계산된 필드들을 추가합니다.
        """
        # 자격요건 데이터 전처리
        date_columns = ['RCRIT_PD_BEGIN_DE', 'RCRIT_PD_END_DE']
        for col in date_columns:
            if col in self.qualifications_df.columns:
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
                self.qualifications_df[col] = pd.to_numeric(
                    self.qualifications_df[col].astype(str).str.replace(',', ''),
                    errors='coerce'
                )
                
        # 기업정보 데이터 전처리
        if 'BSNS_NO' in self.company_df.columns:
            # 설립연도 추출 (사업자등록번호 앞 4자리)
            self.company_df['설립연도'] = self.company_df['BSNS_NO'].str[:4]
            # 업력 계산
            current_year = 2024
            self.company_df['업력'] = current_year - \
                pd.to_numeric(self.company_df['설립연도'], errors='coerce')

    def get_qualification_data(self) -> pd.DataFrame:
        """전처리된 자격요건 데이터를 반환합니다."""
        return self.qualifications_df
    
    def get_company_data(self) -> pd.DataFrame:
        """전처리된 기업정보 데이터를 반환합니다."""
        return self.company_df
    
    def get_available_years(self) -> List[int]:
        """사용 가능한 연도 목록을 반환합니다."""
        return sorted(self.qualifications_df['APPL_YEAR'].unique())
    
    def get_support_categories(self) -> List[str]:
        """지원 분야 카테고리 목록을 반환합니다."""
        return sorted(self.qualifications_df['APPL_REALM_NM'].unique())
    
    def filter_qualifications(
        self,
        year: Optional[int] = None,
        categories: Optional[List[str]] = None,
        company_age: Optional[int] = None,
        is_startup: bool = False,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> pd.DataFrame:
        """자격요건 데이터를 주어진 조건에 따라 필터링합니다.
        
        Args:
            year: 지원년도
            categories: 지원분야 목록
            company_age: 기업 업력
            is_startup: 예비창업자 여부
            min_amount: 최소 지원금액
            max_amount: 최대 지원금액
            
        Returns:
            필터링된 데이터프레임
        """
        filtered_df = self.qualifications_df.copy()
        
        if year:
            filtered_df = filtered_df[filtered_df['APPL_YEAR'] == year]
            
        if categories:
            filtered_df = filtered_df[
                filtered_df['APPL_REALM_NM'].isin(categories)
            ]
            
        if company_age is not None:
            mask = (
                filtered_df['PARTCND_MUMM_PDSMLPZ_CO'] <= company_age
            ) & (
                filtered_df['PARTCND_MXMM_PDSMLPZ_CO'] >= company_age
            )
            filtered_df = filtered_df[mask]
            
        if is_startup:
            filtered_df = filtered_df[
                filtered_df['APPL_TRGET_PREPFNTN_AT'] == 'Y'
            ]
            
        if min_amount:
            filtered_df = filtered_df[
                filtered_df['APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE'] >= min_amount
            ]
            
        if max_amount:
            filtered_df = filtered_df[
                filtered_df['APPL_SCALE_UNIT_PER_MXMM_APPL_PRICE'] <= max_amount
            ]
            
        return filtered_df
    
    def analyze_trends(
        self,
        metric: str,
        group_by: List[str]
    ) -> pd.DataFrame:
        """트렌드 분석을 수행합니다.
        
        Args:
            metric: 분석할 지표
            group_by: 그룹화할 컬럼들
            
        Returns:
            분석 결과 데이터프레임
        """
        if metric in self.qualifications_df.columns:
            return self.qualifications_df.groupby(group_by)[metric].agg([
                'count', 'mean', 'sum'
            ]).round(2)
        return pd.DataFrame()
    
    def get_region_statistics(self) -> pd.DataFrame:
        """지역별 통계를 계산합니다."""
        if 'CMPNY_ADDR' in self.company_df.columns:
            return self.company_df['CMPNY_ADDR'].str.split().str[0].value_counts()
        return pd.Series()
    
    def get_industry_statistics(self) -> pd.DataFrame:
        """업종별 통계를 계산합니다."""
        if 'INDUTY_NM' in self.company_df.columns:
            return self.company_df.groupby('INDUTY_NM').agg({
                'CMPNY_NM': 'count',
                '업력': ['mean', 'min', 'max']
            })
        return pd.DataFrame()

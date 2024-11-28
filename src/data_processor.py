import pandas as pd
from utils.constants import DATA_PATH
from utils.helpers import clean_text, normalize_amount

class DataProcessor:
    """
    데이터 처리를 담당하는 클래스입니다.
    CSV 파일을 읽어 분석 가능한 형태로 전처리합니다.
    """
    def __init__(self):
        # CSV 파일 로드 및 초기 전처리
        self.df = pd.read_csv(DATA_PATH)
        
    def preprocess_support_programs(self):
        """
        지원사업 데이터를 분석하기 좋은 형태로 전처리합니다.
        
        Returns:
            pd.DataFrame: 전처리된 데이터프레임
        """
        # 주요 컬럼 선택
        important_columns = [
            'APPL_REALM_NM',          # 지원부야명
            'BSNS_TASK_NM',           # 사업과제명
            'BSNS_PURPS_CN',          # 사업목적내용
            'APPL_TRGET_RM_CN',       # 지원대상 비고내용
            'PARTCND_CN',             # 참여조건내용
            'APPL_SCALE_TOT_BUDGET_PRICE'  # 지원규모 총예산금액
        ]
        
        # 데이터프레임 복사 및 필요한 컬럼만 선택
        processed_df = self.df[important_columns].copy()
        
        # 텍스트 데이터 전처리
        text_columns = ['BSNS_PURPS_CN', 'APPL_TRGET_RM_CN', 'PARTCND_CN']
        for col in text_columns:
            processed_df[col] = processed_df[col].apply(clean_text)
            
        # 금액 데이터 정규화 (단위: 백만원)
        processed_df['budget_normalized'] = (
            processed_df['APPL_SCALE_TOT_BUDGET_PRICE']
            .apply(normalize_amount) / 1_000_000
        )
        
        # 결측치 처리
        processed_df = processed_df.fillna('')
        
        return processed_df

    def extract_program_features(self, text):
        """
        텍스트에서 주요 특성을 추출합니다.
        
        Args:
            text (str): 분석할 텍스트
        
        Returns:
            dict: 추출된 특성들을 담은 사전
        """
        from utils.constants import BUSINESS_STAGES, BUSINESS_SECTORS
        
        features = {
            'stage': [],
            'sector': []
        }
        
        # 사업 단계 추출
        for stage, keywords in BUSINESS_STAGES.items():
            if any(keyword in text for keyword in keywords):
                features['stage'].append(stage)
                
        # 사업 분야 추출
        for sector, keywords in BUSINESS_SECTORS.items():
            if any(keyword in text for keyword in keywords):
                features['sector'].append(sector)
                
        return features

import pandas as pd
import numpy as np
import streamlit as st

class DataProcessor:
    def __init__(self):
        # 데이터 로드 및 초기 전처리
        self.df = pd.read_csv('KS_SPORTS_INDUST_APPL_BSNS_APPL_QUALF_INFO_202409.csv')
        
    def preprocess_support_programs(self):
        """지원사업 데이터를 분석하기 좋은 형태로 전처리합니다."""
        # 주요 컬럼 선택
        important_columns = [
            'APPL_REALM_NM',          # 지원부야명
            'BSNS_TASK_NM',           # 사업과제명
            'BSNS_PURPS_CN',          # 사업목적내용
            'APPL_TRGET_RM_CN',       # 지원대상 비고내용
            'PARTCND_CN',             # 참여조건내용
            'APPL_SCALE_TOT_BUDGET_PRICE'  # 지원규모 총예산금액
        ]
        
        processed_df = self.df[important_columns].copy()
        
        # 결측치 처리
        processed_df = processed_df.fillna('')
        
        # 지원금액 정규화 (단위: 백만원)
        processed_df['budget_normalized'] = processed_df['APPL_SCALE_TOT_BUDGET_PRICE'] / 1_000_000
        
        return processed_df

    def extract_key_features(self, text):
        """텍스트에서 주요 특성을 추출합니다."""
        # 주요 키워드 사전 정의
        keywords = {
            'stage': ['예비창업', '초기창업', '도약', '성장'],
            'sector': ['용품제조', '서비스', '시설운영'],
            'scale': ['소상공인', '중소기업', '중견기업']
        }
        
        features = {category: [] for category in keywords}
        
        # 각 카테고리별 키워드 매칭
        for category, words in keywords.items():
            for word in words:
                if word in text:
                    features[category].append(word)
        
        return features

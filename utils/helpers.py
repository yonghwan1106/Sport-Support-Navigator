import re
from typing import Dict, List, Any

def clean_text(text: str) -> str:
    """텍스트 데이터를 전처리합니다."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'\s+', ' ', text)  # 연속된 공백 제거
    text = text.strip()  # 앞뒤 공백 제거
    return text

def normalize_amount(amount: Any) -> float:
    """금액 데이터를 정규화합니다."""
    if isinstance(amount, str):
        # 문자열에서 숫자만 추출
        amount = re.sub(r'[^\d.]', '', amount)
        try:
            return float(amount)
        except ValueError:
            return 0.0
    elif isinstance(amount, (int, float)):
        return float(amount)
    return 0.0

def calculate_similarity_score(profile: Dict, criteria: Dict) -> float:
    """프로파일과 기준 간의 유사도를 계산합니다."""
    score = 0.0
    total_weight = 0.0
    
    for key, weight in criteria.items():
        if key in profile and key in criteria:
            if isinstance(profile[key], str) and isinstance(criteria[key], str):
                # 문자열 유사도 계산
                score += weight * (1 if profile[key] == criteria[key] else 0)
            elif isinstance(profile[key], (int, float)) and isinstance(criteria[key], (int, float)):
                # 수치 유사도 계산
                max_value = max(profile[key], criteria[key])
                min_value = min(profile[key], criteria[key])
                score += weight * (min_value / max_value if max_value > 0 else 1)
        total_weight += weight
    
    return score / total_weight if total_weight > 0 else 0.0

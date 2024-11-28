# 자주 사용되는 상수값들을 정의합니다
DATA_PATH = "data/KS_SPORTS_INDUST_APPL_BSNS_APPL_QUALF_INFO_202409.csv"

# 매칭 시스템에서 사용할 가중치 설정
MATCHING_WEIGHTS = {
    'business_relevance': 0.4,
    'support_scale': 0.3,
    'requirements_match': 0.3
}

# 사업 단계별 키워드 정의
BUSINESS_STAGES = {
    'preliminary': ['예비창업', '준비단계', '아이디어'],
    'initial': ['초기창업', '시작단계', '1년차'],
    'growth': ['성장', '도약', '확장'],
    'stable': ['안정화', '성숙', '정착']
}

# 지원 분야 키워드 정의
BUSINESS_SECTORS = {
    'manufacturing': ['제조', '용품', '장비'],
    'service': ['서비스', '교육', '컨설팅'],
    'facility': ['시설', '공간', '센터']
}

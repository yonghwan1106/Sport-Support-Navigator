# 스포츠산업 지원사업 분석 시스템

## 프로젝트 소개

이 프로젝트는 국민체육진흥공단의 스포츠산업 지원사업 데이터를 분석하고 시각화하는 웹 기반 분석 시스템입니다. 지원사업 자격요건 정보와 지원기업 데이터를 통합적으로 분석하여, 기업들이 적합한 지원사업을 찾고 전략적인 의사결정을 할 수 있도록 도와줍니다.

## 주요 기능

### 1. 지원사업 검색 (Program Search)
사용자는 다양한 조건을 기반으로 적합한 지원사업을 검색할 수 있습니다:
- 연도별, 분야별 지원사업 필터링
- 기업 조건(업력, 규모 등)에 따른 맞춤형 검색
- 지원금액 범위 설정
- 실시간 검색 결과 시각화

### 2. 기업 분석 (Company Analysis)
지원기업들의 특성과 패턴을 분석합니다:
- 업종별 기업 분포 분석
- 지역별 기업 현황 매핑
- 기업 규모 및 업력 분석
- 상세 기업정보 조회

### 3. 트렌드 분석 (Trend Analysis)
시계열 데이터를 기반으로 변화 추이를 분석합니다:
- 연도별 지원금액 추이 분석
- 자격요건 변화 패턴 분석
- 기업 참여 트렌드 분석
- 주요 지표의 시계열적 변화

## 기술 스택

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Data Visualization**: Plotly
- **Development Tools**: Black, Pytest
- **Version Control**: Git

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/your-username/sports-industry-support.git
cd sports-industry-support
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

## 사용 방법

1. 애플리케이션 실행
```bash
streamlit run app.py
```

2. 웹 브라우저에서 접속
- 기본적으로 `http://localhost:8501`에서 애플리케이션에 접근할 수 있습니다
- 시작 페이지에서 주요 기능과 사용법을 확인할 수 있습니다

## 프로젝트 구조

```
sports-industry-support/
├── data/                                  # 데이터 디렉토리
│   ├── program_qualifications.csv         # 지원사업 자격요건 정보
│   ├── program_qualifications_columns.csv # 자격요건 컬럼 정의
│   ├── company_info.csv                  # 지원기업 정보
│   └── company_info_columns.csv          # 기업정보 컬럼 정의
├── pages/                                # 스트림릿 페이지
│   ├── 1_program_search.py              # 지원사업 검색 페이지
│   ├── 2_company_analysis.py            # 기업 분석 페이지
│   └── 3_trend_analysis.py              # 트렌드 분석 페이지
├── utils.py                              # 유틸리티 함수
├── app.py                                # 메인 애플리케이션
├── requirements.txt                      # 의존성 패키지 목록
└── README.md                            # 프로젝트 문서
```

## 데이터 소스

이 프로젝트는 다음 데이터를 활용합니다:
- 스포츠산업 지원사업 자격요건 정보
- 스포츠산업 지원사업 참여 기업 정보

## 개발 가이드라인

1. 코드 스타일
- Black 포맷터를 사용하여 일관된 코드 스타일 유지
- 타입 힌팅을 적극적으로 활용
- 주석과 문서화 철저히 수행

2. 테스트
- Pytest를 사용한 단위 테스트 작성
- 새로운 기능 추가 시 관련 테스트 코드 포함

3. 버전 관리
- 의미 있는 커밋 메시지 작성
- 기능별 브랜치 생성 및 관리
- Pull Request를 통한 코드 리뷰

## 기여 방법

1. 이슈 등록
- 버그 리포트 또는 기능 제안을 이슈로 등록
- 명확한 재현 방법 또는 요구사항 기술

2. Pull Request
- 기능 개발을 위한 새로운 브랜치 생성
- 개발 완료 후 Pull Request 생성
- 코드 리뷰 진행

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 문의 및 지원

프로젝트 관련 문의나 지원이 필요한 경우:
- GitHub Issues를 통한 질문 등록
- 프로젝트 관리자 이메일 문의

## 감사의 글

이 프로젝트는 국민체육진흥공단의 공공데이터를 활용하여 제작되었습니다. 데이터 제공에 감사드립니다.

---
이 프로젝트는 2024년 국민체육진흥공단 공공데이터 활용 경진대회 출품작입니다.

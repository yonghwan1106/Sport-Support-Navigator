import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ProgramMatcher:
    def __init__(self, processed_data):
        """매칭 엔진 초기화
        
        processed_data: DataProcessor에서 전처리된 데이터프레임
        """
        self.data = processed_data
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english'
        )
        # 지원사업 설명 텍스트를 벡터화
        self.program_vectors = self._vectorize_programs()
        # 특성별 가중치 초기화
        self.feature_weights = {
            'business_relevance': 0.4,  # 사업 관련성
            'support_scale': 0.3,      # 지원 규모
            'requirements_match': 0.3   # 자격요건 부합도
        }
    
    def _vectorize_programs(self):
        """지원사업 설명을 벡터화합니다."""
        # 사업 설명과 지원대상 정보를 결합
        program_texts = (self.data['BSNS_PURPS_CN'] + ' ' + 
                        self.data['APPL_TRGET_RM_CN'])
        return self.vectorizer.fit_transform(program_texts)
    
    def _calculate_business_relevance(self, user_profile):
        """사용자 프로필과 사업 간의 관련성을 계산합니다."""
        # 사용자 프로필을 동일한 벡터 공간으로 변환
        user_vector = self.vectorizer.transform([user_profile['description']])
        # 코사인 유사도 계산
        similarities = cosine_similarity(user_vector, self.program_vectors)
        return similarities.flatten()
    
    def _calculate_support_scale_match(self, user_profile):
        """지원 규모의 적절성을 계산합니다."""
        user_scale = user_profile.get('desired_support_scale', 0)
        program_scales = self.data['budget_normalized'].values
        
        # 지원 규모 차이를 정규화하여 점수 계산
        scale_differences = np.abs(program_scales - user_scale)
        max_diff = np.max(scale_differences)
        return 1 - (scale_differences / max_diff if max_diff > 0 else 0)
    
    def _calculate_requirements_match(self, user_profile):
        """자격요건 부합도를 계산합니다."""
        # Linear Latent Intervention 적용
        requirement_scores = np.zeros(len(self.data))
        
        for idx, program in self.data.iterrows():
            score = 0
            requirements = program['PARTCND_CN']
            
            # 사업 단계 매칭
            if user_profile['stage'] in requirements:
                score += 0.4
            
            # 기업 규모 매칭
            if user_profile['scale'] in requirements:
                score += 0.3
                
            # 업종 매칭
            if user_profile['sector'] in requirements:
                score += 0.3
                
            requirement_scores[idx] = score
            
        return requirement_scores
    
    def find_matches(self, user_profile, top_n=5):
        """사용자 프로필에 가장 적합한 지원사업을 찾습니다."""
        # 각 특성별 점수 계산
        relevance_scores = self._calculate_business_relevance(user_profile)
        scale_scores = self._calculate_support_scale_match(user_profile)
        requirement_scores = self._calculate_requirements_match(user_profile)
        
        # 가중 평균으로 최종 점수 계산
        final_scores = (
            self.feature_weights['business_relevance'] * relevance_scores +
            self.feature_weights['support_scale'] * scale_scores +
            self.feature_weights['requirements_match'] * requirement_scores
        )
        
        # 상위 N개 프로그램 선정
        top_indices = np.argsort(final_scores)[-top_n:][::-1]
        
        # 결과 포맷팅
        matches = []
        for idx in top_indices:
            program = self.data.iloc[idx]
            match_info = {
                'program_name': program['BSNS_TASK_NM'],
                'score': final_scores[idx],
                'relevance_score': relevance_scores[idx],
                'scale_score': scale_scores[idx],
                'requirement_score': requirement_scores[idx],
                'details': program.to_dict()
            }
            matches.append(match_info)
            
        return matches

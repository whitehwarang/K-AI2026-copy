# K-AI2026

대한민국 AI 행동계획 2026 대시보드 (비공식)

이 저장소는 기존 HTML/JavaScript 기반 대시보드를 Python Streamlit 애플리케이션으로 전환한 버전을 포함합니다. 원천 데이터(`data/*.json`)는 그대로 사용하며, Streamlit UI에서 과제·부처·일정·글로벌 사례·참고자료·AI 페르소나 평가를 탐색할 수 있습니다.

## Streamlit 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 Streamlit이 안내하는 로컬 주소(기본값: <http://localhost:8501>)를 열면 됩니다.

## 주요 기능

- 99개 실천과제와 326개 정책권고 KPI 요약
- 정책축/전략분야/부처별 권고 현황 시각화
- 검색어, 정책축, 전략분야, 담당 부처 기반 실천과제 필터링
- 부처별 권고 목록과 임박/주의 권고 확인
- 이행 일정, 글로벌 AI 정책 사례, 참고자료/각주 검색
- 과제별 AI 페르소나 평가 결과 조회
- 정책축 → 전략분야 → 과제 → 부처 Sankey 흐름도

## 관련 링크

- [(대통령직속) 국가인공지능전략위원회](https://www.aikorea.go.kr/)
- [대한민국 인공지능 행동계획 2026~2028](https://www.aikorea.go.kr/web/board/brdDetail.do?menu_cd=000011&num=328&currentPage=1&searchData=&searchText=)

> 이 페이지는 공식 페이지나 공식 결과가 아닙니다. 공식 배포 문서와 내용은 관련 링크를 참고하시기 바랍니다.

---
Jonghong Jeon (hollobit@etri.re.kr)

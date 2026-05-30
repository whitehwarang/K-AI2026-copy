# K-AI2026

지식재산처 AI 실행과제 내부 대시보드 (임시 Streamlit 버전)

기존 국가AI전략위 중심 HTML/JavaScript 대시보드를 지식재산처 내부용 Streamlit 애플리케이션으로 개편했습니다. 아직 실제 업무 데이터가 없다는 전제에 맞춰 `model_config.json`으로 화면 컬럼과 필터 기준을 정의하고, `data/ip_eav_sample.json`에 EAV(Entity-Attribute-Value) 형식의 가짜 데이터를 넣어 임시 화면을 구성합니다.

## Streamlit 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 Streamlit이 안내하는 로컬 주소(기본값: <http://localhost:8501>)를 열면 됩니다.

## 현재 화면 구성

- **종합**: 전체 과제, 담당 국·과, 위험도 등 내부 관리 KPI와 `model_config.json`의 종합 컬럼 기준 과제 현황
- **과제 탐색**: `model_config.json`의 필터/검색/컬럼 설정을 따르는 과제 검색 화면
- **조직별**: 기존 부처별 화면을 지식재산처 내부 조직(국·과)별 과제 현황 화면으로 변경

## 데이터 모델

- `model_config.json`: 엔티티, 속성, 화면별 컬럼, 필터, 검색 대상 정의
- `data/ip_eav_sample.json`: 실제 데이터 적재 전 화면 검증을 위한 EAV 샘플 데이터
- 향후 실제 데이터는 `entities`와 `attributes` 배열에 엔티티와 속성값을 추가하는 방식으로 확장할 수 있습니다.

> 이 저장소의 현재 데이터는 시연용 가짜 데이터이며 공식 자료가 아닙니다.

---
Jonghong Jeon (hollobit@etri.re.kr)

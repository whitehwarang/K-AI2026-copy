from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).parent
MODEL_CONFIG_PATH = ROOT / "model_config.json"

st.set_page_config(
    page_title="지식재산처 AI과제 관리 대시보드",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    .small-muted {color:#64748b; font-size:0.9rem;}
    .task-title {font-weight:700; color:#0f172a;}
    .rec-box {border-left: 4px solid #2563eb; padding: .75rem 1rem; background:#f8fafc; border-radius: 8px; margin-bottom:.6rem;}
    .schema-chip {display:inline-block; margin:.15rem .25rem .15rem 0; padding:.2rem .55rem; border:1px solid #dbeafe; border-radius:999px; background:#eff6ff; color:#1e40af; font-size:.85rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_model_config() -> dict[str, Any]:
    with MODEL_CONFIG_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def schema_fields(config: dict[str, Any], entity_type: str) -> list[str]:
    return [field["field"] for field in config["data_model"].get(entity_type, [])]


def make_eav_entity(entity_type: str, entity_id: str, values: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"entity_type": entity_type, "entity_id": entity_id, "attribute": attribute, "value": value}
        for attribute, value in values.items()
    ]


@st.cache_data(show_spinner=False)
def load_eav_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    """임시 샘플 데이터를 EAV(Entity-Attribute-Value) 형태로 생성합니다.

    실제 저장소가 붙기 전까지 model_config.json의 필드명을 그대로 attribute로 사용해
    화면 구조와 필터를 검증할 수 있게 합니다.
    """
    samples: list[dict[str, Any]] = []
    samples.extend(
        make_eav_entity(
            "사업",
            "BIZ-2026-001",
            {
                "부서(국)": "지식재산정보국",
                "부서(과)": "지식재산데이터관리과",
                "세부사업명": "지식재산 데이터 활용 기반 구축",
                "내역사업명": "AI 학습용 IP 데이터셋 정비",
                "AI과제명": "특허·상표 심사 데이터 품질 자동진단",
                "담당자": "김지현",
                "사업비(백만원)": 850,
                "과제설명": "심사·출원 데이터의 누락, 중복, 비식별화 상태를 AI로 점검하고 학습 가능한 내부 표준 데이터셋을 구축합니다.",
                "진행상태": "진행중",
                "국정과제여부": "예",
                "국정과제번호(??-?)": "12-3",
                "AI행동계획여부": "예",
                "AI행동계획과제번호": 24,
                "AI행동계획권고번호": 81,
            },
        )
    )
    samples.extend(
        make_eav_entity(
            "사업",
            "BIZ-2026-002",
            {
                "부서(국)": "디지털융합심사국",
                "부서(과)": "인공지능빅데이터심사과",
                "세부사업명": "AI 기반 심사 지원체계 고도화",
                "내역사업명": "선행기술 후보 추천 모델 실증",
                "AI과제명": "인공지능·빅데이터 분야 선행기술 탐색 보조",
                "담당자": "박민수",
                "사업비(백만원)": 1_250,
                "과제설명": "심사관 질의 의도와 청구항 핵심구성을 반영해 선행기술 후보군과 유사 근거를 추천하는 내부 PoC입니다.",
                "진행상태": "검토중",
                "국정과제여부": "아니오",
                "국정과제번호(??-?)": "",
                "AI행동계획여부": "예",
                "AI행동계획과제번호": 31,
                "AI행동계획권고번호": 104,
            },
        )
    )
    samples.extend(
        make_eav_entity(
            "사업",
            "BIZ-2026-003",
            {
                "부서(국)": "지식재산보호협력국",
                "부서(과)": "상표특별사법경찰과",
                "세부사업명": "지식재산 침해 대응 역량 강화",
                "내역사업명": "온라인 위조상품 탐지 자동화",
                "AI과제명": "상표권 침해 의심 게시물 AI 탐지",
                "담당자": "이서연",
                "사업비(백만원)": 640,
                "과제설명": "오픈마켓·SNS 게시물의 이미지와 문구를 분석해 위조상품 의심 건을 선별하고 조사 우선순위를 제안합니다.",
                "진행상태": "계획중",
                "국정과제여부": "예",
                "국정과제번호(??-?)": "18-2",
                "AI행동계획여부": "아니오",
                "AI행동계획과제번호": None,
                "AI행동계획권고번호": None,
            },
        )
    )
    samples.extend(
        make_eav_entity(
            "사업",
            "BIZ-2026-004",
            {
                "부서(국)": "기계금속심사국",
                "부서(과)": "자동차심사과",
                "세부사업명": "첨단산업 심사품질 제고",
                "내역사업명": "모빌리티 특허 분류 자동화",
                "AI과제명": "자율주행·전동화 기술분류 추천",
                "담당자": "최도윤",
                "사업비(백만원)": 410,
                "과제설명": "자동차 분야 출원 문헌을 기술 세부 분야별로 자동 분류하고 유사 심사 사례를 연결합니다.",
                "진행상태": "완료",
                "국정과제여부": "아니오",
                "국정과제번호(??-?)": "",
                "AI행동계획여부": "예",
                "AI행동계획과제번호": 42,
                "AI행동계획권고번호": 139,
            },
        )
    )
    samples.extend(
        make_eav_entity(
            "27년 예산안",
            "BUD-2027-001",
            {
                "부서(국)": "지식재산정보국",
                "부서(과)": "지식재산정보시스템과",
                "세부사업명": "차세대 지식재산 행정 플랫폼",
                "내역사업명": "AI 업무비서 및 검색 고도화",
                "AI과제명": "지식재산처 내부 AI 업무비서 구축",
                "담당자": "정하늘",
                "사업비(백만원)": 1_800,
                "과제설명": "법령, 심사지침, 내부 매뉴얼을 기반으로 담당자 질의응답과 문서 초안을 지원하는 RAG 기반 업무비서입니다.",
                "국정과제여부": "예",
                "국정과제번호(??-?)": "12-3",
                "AI행동계획여부": "예",
                "AI행동계획과제번호": 27,
                "AI행동계획권고번호": 88,
            },
        )
    )
    samples.extend(
        make_eav_entity(
            "27년 예산안",
            "BUD-2027-002",
            {
                "부서(국)": "상표디자인심사국",
                "부서(과)": "디자인심사정책과",
                "세부사업명": "디자인 심사 디지털 전환",
                "내역사업명": "이미지 유사도 검색 인프라",
                "AI과제명": "디자인 유사 이미지 탐색 모델 확산",
                "담당자": "한유진",
                "사업비(백만원)": 920,
                "과제설명": "디자인 출원 이미지와 공개 디자인 자료 간 유사도를 계산해 심사관의 검색 시간을 단축합니다.",
                "국정과제여부": "아니오",
                "국정과제번호(??-?)": "",
                "AI행동계획여부": "예",
                "AI행동계획과제번호": 36,
                "AI행동계획권고번호": 118,
            },
        )
    )

    configured_attributes = {
        entity_type: set(schema_fields(config, entity_type)) for entity_type in config.get("data_model", {})
    }
    return [
        row
        for row in samples
        if row["attribute"] in configured_attributes.get(row["entity_type"], set())
    ]


def eav_to_records(eav_rows: list[dict[str, Any]], config: dict[str, Any], entity_type: str) -> pd.DataFrame:
    fields = schema_fields(config, entity_type)
    records: dict[str, dict[str, Any]] = {}
    for row in eav_rows:
        if row["entity_type"] != entity_type:
            continue
        entity_id = row["entity_id"]
        records.setdefault(entity_id, {"ID": entity_id})
        records[entity_id][row["attribute"]] = row["value"]

    ordered_rows = []
    for entity_id, values in records.items():
        ordered_rows.append({"ID": entity_id, **{field: values.get(field) for field in fields}})
    return pd.DataFrame(ordered_rows, columns=["ID", *fields])


def normalize_money(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def render_header(biz_df: pd.DataFrame, budget_df: pd.DataFrame, organizations: dict[str, list[str]]) -> None:
    st.title("🏛️ 지식재산처 AI과제 관리 대시보드")
    st.caption("model_config.json 기반 EAV 임시 데이터로 구성한 지식재산처 내부 AI과제 관리 화면입니다.")
    total_budget = normalize_money(biz_df.get("사업비(백만원)", pd.Series(dtype="float64"))).sum()
    next_budget = normalize_money(budget_df.get("사업비(백만원)", pd.Series(dtype="float64"))).sum()
    cols = st.columns(4)
    cols[0].metric("AI과제", f"{len(biz_df):,}개")
    cols[1].metric("27년 예산안", f"{len(budget_df):,}건")
    cols[2].metric("사업비", f"{total_budget:,.0f}백만원")
    cols[3].metric("내부 조직", f"{len(organizations):,}개 국")
    st.caption(f"27년 예산안 합계: {next_budget:,.0f}백만원 · 실제 데이터 연계 전까지 샘플 데이터로 표시됩니다.")


def render_schema_note(config: dict[str, Any], entity_type: str) -> None:
    fields = schema_fields(config, entity_type)
    chips = "".join(f"<span class='schema-chip'>{field}</span>" for field in fields)
    st.markdown(f"**{entity_type} 표시 필드(model_config.json 기준)**  ")
    st.markdown(chips, unsafe_allow_html=True)


def render_overview(config: dict[str, Any], biz_df: pd.DataFrame, budget_df: pd.DataFrame) -> None:
    st.subheader("종합 현황")
    render_schema_note(config, "사업")

    left, right = st.columns([1, 1])
    with left:
        status_counts = biz_df.groupby("진행상태", dropna=False, as_index=False).size().rename(columns={"size": "과제 수"})
        st.plotly_chart(px.pie(status_counts, values="과제 수", names="진행상태", hole=0.45), use_container_width=True)
    with right:
        guk_counts = biz_df.groupby("부서(국)", dropna=False, as_index=False).size().rename(columns={"size": "과제 수"}).sort_values("과제 수")
        st.plotly_chart(px.bar(guk_counts, x="과제 수", y="부서(국)", orientation="h", text="과제 수"), use_container_width=True)

    budget_by_guk = biz_df.assign(**{"사업비(백만원)": normalize_money(biz_df["사업비(백만원)"])}).groupby("부서(국)", as_index=False)["사업비(백만원)"].sum()
    st.markdown("#### 국별 사업비(백만원)")
    st.plotly_chart(px.bar(budget_by_guk.sort_values("사업비(백만원)", ascending=False), x="부서(국)", y="사업비(백만원)", text="사업비(백만원)"), use_container_width=True)

    st.markdown("#### AI과제 목록")
    st.dataframe(biz_df, use_container_width=True, hide_index=True)

    st.markdown("#### 27년 예산안")
    render_schema_note(config, "27년 예산안")
    st.dataframe(budget_df, use_container_width=True, hide_index=True)


def filter_records(df: pd.DataFrame, query: str, selected_guk: list[str], selected_gwa: list[str], selected_statuses: list[str]) -> pd.DataFrame:
    filtered = df.copy()
    q = query.strip().lower()
    if q:
        mask = filtered.astype(str).agg(" ".join, axis=1).str.lower().str.contains(q, regex=False)
        filtered = filtered[mask]
    if selected_guk:
        filtered = filtered[filtered["부서(국)"].isin(selected_guk)]
    if selected_gwa:
        filtered = filtered[filtered["부서(과)"].isin(selected_gwa)]
    if selected_statuses and "진행상태" in filtered.columns:
        filtered = filtered[filtered["진행상태"].isin(selected_statuses)]
    return filtered


def render_tasks(config: dict[str, Any], biz_df: pd.DataFrame, budget_df: pd.DataFrame) -> None:
    st.subheader("과제 탐색")
    entity_type = st.radio("조회 대상", ["사업", "27년 예산안"], horizontal=True)
    current_df = biz_df if entity_type == "사업" else budget_df

    with st.sidebar:
        st.markdown("### 필터")
        query = st.text_input("검색어", placeholder="예: 심사, 상표, 데이터, 담당자")
        selected_guk = st.multiselect("부서(국)", sorted(current_df["부서(국)"].dropna().unique()))
        selected_gwa = st.multiselect("부서(과)", sorted(current_df["부서(과)"].dropna().unique()))
        statuses = sorted(current_df["진행상태"].dropna().unique()) if "진행상태" in current_df.columns else []
        selected_statuses = st.multiselect("진행상태", statuses) if statuses else []

    filtered = filter_records(current_df, query, selected_guk, selected_gwa, selected_statuses)
    render_schema_note(config, entity_type)
    st.caption(f"검색 결과: {len(filtered):,}건")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    for record in filtered.to_dict("records"):
        title = record.get("AI과제명") or record.get("내역사업명") or record["ID"]
        with st.expander(f"{record['ID']} · {title}"):
            cols = st.columns(2)
            cols[0].markdown(f"**부서(국):** {record.get('부서(국)', '')}")
            cols[0].markdown(f"**부서(과):** {record.get('부서(과)', '')}")
            cols[1].markdown(f"**담당자:** {record.get('담당자', '')}")
            cols[1].markdown(f"**사업비(백만원):** {record.get('사업비(백만원)', '')}")
            st.markdown("**과제설명**")
            st.write(record.get("과제설명", ""))
            detail = pd.DataFrame([{"항목": key, "값": value} for key, value in record.items()])
            st.dataframe(detail, use_container_width=True, hide_index=True)


def render_organizations(organizations: dict[str, list[str]], biz_df: pd.DataFrame, budget_df: pd.DataFrame) -> None:
    st.subheader("조직별 실행 현황")
    st.caption("기존 부처별 보기를 지식재산처 내부 조직(국·과) 단위로 재구성했습니다.")

    selected_guk = st.selectbox("국 선택", list(organizations))
    gwa_options = organizations[selected_guk]
    selected_gwa = st.selectbox("과 선택", ["전체", *gwa_options])

    combined = pd.concat(
        [biz_df.assign(구분="사업"), budget_df.assign(구분="27년 예산안")],
        ignore_index=True,
        sort=False,
    )
    filtered = combined[combined["부서(국)"] == selected_guk]
    if selected_gwa != "전체":
        filtered = filtered[filtered["부서(과)"] == selected_gwa]

    budget_sum = normalize_money(filtered.get("사업비(백만원)", pd.Series(dtype="float64"))).sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("관리 항목", f"{len(filtered):,}건")
    col2.metric("사업비", f"{budget_sum:,.0f}백만원")
    col3.metric("소속 과", f"{len(gwa_options):,}개")

    if filtered.empty:
        st.info("선택한 조직에 연결된 임시 과제가 없습니다.")
        return

    by_gwa = filtered.groupby(["부서(과)", "구분"], dropna=False, as_index=False).size().rename(columns={"size": "건수"})
    st.plotly_chart(px.bar(by_gwa, x="부서(과)", y="건수", color="구분", text="건수", barmode="group"), use_container_width=True)
    st.dataframe(filtered, use_container_width=True, hide_index=True)


def render_eav_debug(eav_rows: list[dict[str, Any]]) -> None:
    with st.expander("EAV 원천 행 보기"):
        st.caption("entity_type, entity_id, attribute, value 구조로 임시 구성한 데이터입니다.")
        st.dataframe(pd.DataFrame(eav_rows), use_container_width=True, hide_index=True)


def main() -> None:
    config = load_model_config()
    organizations = config.get("organizations", {})
    eav_rows = load_eav_rows(config)
    biz_df = eav_to_records(eav_rows, config, "사업")
    budget_df = eav_to_records(eav_rows, config, "27년 예산안")

    render_header(biz_df, budget_df, organizations)

    tab_names = ["종합", "과제 탐색", "조직별"]
    tabs = st.tabs(tab_names)
    with tabs[0]:
        render_overview(config, biz_df, budget_df)
        render_eav_debug(eav_rows)
    with tabs[1]:
        render_tasks(config, biz_df, budget_df)
    with tabs[2]:
        render_organizations(organizations, biz_df, budget_df)


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "model_config.json"
SAMPLE_DATA_PATH = ROOT / "data" / "ip_eav_sample.json"

st.set_page_config(
    page_title="지식재산처 AI 실행과제 내부 대시보드",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    .notice-box {border-left: 4px solid #7c3aed; background: #f5f3ff; padding: .85rem 1rem; border-radius: .75rem; color: #312e81;}
    .task-card {border: 1px solid #e5e7eb; border-radius: 14px; padding: 1rem; background: #ffffff; margin-bottom: .75rem;}
    .muted {color: #64748b; font-size: .92rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(show_spinner=False)
def load_config() -> dict[str, Any]:
    return load_json(CONFIG_PATH)


@st.cache_data(show_spinner=False)
def load_eav_data() -> dict[str, Any]:
    return load_json(SAMPLE_DATA_PATH)


def attribute_labels(config: dict[str, Any]) -> dict[str, str]:
    return {
        attribute["key"]: attribute["label"]
        for attribute in config.get("attributes", {}).get("task", [])
    }


def materialize_tasks(config: dict[str, Any], eav_data: dict[str, Any]) -> pd.DataFrame:
    task_entity_ids = [
        entity["entity_id"]
        for entity in eav_data.get("entities", [])
        if entity.get("entity_type") == "task"
    ]
    rows: dict[str, dict[str, Any]] = {
        entity_id: {"entity_id": entity_id} for entity_id in task_entity_ids
    }
    allowed_attributes = {
        attribute["key"] for attribute in config.get("attributes", {}).get("task", [])
    }
    for item in eav_data.get("attributes", []):
        entity_id = item.get("entity_id")
        attribute = item.get("attribute")
        if entity_id in rows and attribute in allowed_attributes:
            rows[entity_id][attribute] = item.get("value")
    frame = pd.DataFrame(rows.values())
    if frame.empty:
        return frame
    for attribute in allowed_attributes:
        if attribute not in frame.columns:
            frame[attribute] = ""
    if "progress" in frame.columns:
        frame["progress"] = pd.to_numeric(frame["progress"], errors="coerce").fillna(0).astype(int)
    return frame


def columns_for_view(config: dict[str, Any], view_name: str) -> list[str]:
    return config.get("views", {}).get(view_name, {}).get("columns", [])


def label_dataframe(frame: pd.DataFrame, config: dict[str, Any], columns: list[str]) -> pd.DataFrame:
    labels = attribute_labels(config)
    available_columns = [column for column in columns if column in frame.columns]
    return frame[available_columns].rename(columns=labels)


def render_header(config: dict[str, Any]) -> None:
    app_info = config.get("app", {})
    st.title(app_info.get("title", "지식재산처 AI 실행과제 내부 대시보드"))
    st.caption(app_info.get("subtitle", "EAV 데이터 모델 기반 내부 대시보드"))
    st.markdown(
        f"<div class='notice-box'>📌 {app_info.get('notice', '현재 화면은 임시 데이터로 구성되어 있습니다.')}</div>",
        unsafe_allow_html=True,
    )


def render_overview(config: dict[str, Any], tasks: pd.DataFrame) -> None:
    st.subheader("종합")
    if tasks.empty:
        st.info("표시할 과제 데이터가 없습니다.")
        return

    metric_cols = st.columns(4)
    metric_cols[0].metric("전체 과제", f"{len(tasks):,}개")
    metric_cols[1].metric("담당 국", f"{tasks['lead_bureau'].nunique():,}개")
    metric_cols[2].metric("담당 과", f"{tasks['lead_division'].nunique():,}개")
    metric_cols[3].metric("상위험 과제", f"{(tasks['risk_level'] == '상').sum():,}개")

    left, right = st.columns(2)
    with left:
        bureau_counts = tasks.groupby("lead_bureau", as_index=False).size().rename(columns={"size": "과제 수"})
        st.plotly_chart(
            px.bar(bureau_counts, x="lead_bureau", y="과제 수", text="과제 수", labels={"lead_bureau": "주관국"}),
            use_container_width=True,
        )
    with right:
        status_counts = tasks.groupby("status", as_index=False).size().rename(columns={"size": "과제 수"})
        st.plotly_chart(
            px.pie(status_counts, values="과제 수", names="status", hole=0.45),
            use_container_width=True,
        )

    st.markdown("#### 주요 과제 현황")
    overview_columns = columns_for_view(config, "overview")
    st.dataframe(label_dataframe(tasks, config, overview_columns), use_container_width=True, hide_index=True)


def unique_values(tasks: pd.DataFrame, column: str) -> list[str]:
    if column not in tasks.columns:
        return []
    return sorted(str(value) for value in tasks[column].dropna().unique() if str(value).strip())


def filter_tasks(config: dict[str, Any], tasks: pd.DataFrame) -> pd.DataFrame:
    explorer_config = config.get("views", {}).get("task_explorer", {})
    filter_attributes = explorer_config.get("filter_attributes", [])
    search_attributes = explorer_config.get("search_attributes", [])

    with st.sidebar:
        st.markdown("### 과제 탐색 필터")
        query = st.text_input("검색어", placeholder="예: 선행기술, 상표, 정보관리")
        selected_filters: dict[str, list[str]] = {}
        labels = attribute_labels(config)
        for attribute in filter_attributes:
            options = unique_values(tasks, attribute)
            selected_filters[attribute] = st.multiselect(labels.get(attribute, attribute), options)

    filtered = tasks.copy()
    for attribute, selected_values in selected_filters.items():
        if selected_values and attribute in filtered.columns:
            filtered = filtered[filtered[attribute].astype(str).isin(selected_values)]

    if query.strip():
        lowered_query = query.strip().lower()
        available_search_columns = [column for column in search_attributes if column in filtered.columns]
        search_blob = filtered[available_search_columns].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
        filtered = filtered[search_blob.str.contains(lowered_query, regex=False)]
    return filtered


def render_task_explorer(config: dict[str, Any], tasks: pd.DataFrame) -> None:
    st.subheader("과제 탐색")
    if tasks.empty:
        st.info("표시할 과제 데이터가 없습니다.")
        return

    filtered = filter_tasks(config, tasks)
    st.caption(f"검색 결과: {len(filtered):,}개 과제")
    explorer_columns = columns_for_view(config, "task_explorer")
    st.dataframe(label_dataframe(filtered, config, explorer_columns), use_container_width=True, hide_index=True)

    st.markdown("#### 상세 보기")
    for _, task in filtered.iterrows():
        title = f"{task.get('task_no', '')} · {task.get('title', '')}"
        with st.expander(title):
            col1, col2, col3 = st.columns(3)
            col1.metric("주관국", task.get("lead_bureau", "-"))
            col2.metric("주관과", task.get("lead_division", "-"))
            col3.metric("진척률", f"{task.get('progress', 0)}%")
            st.write(task.get("description", ""))
            st.markdown(f"**다음 조치:** {task.get('next_action', '')}")


def render_organization(config: dict[str, Any], tasks: pd.DataFrame) -> None:
    st.subheader("조직별")
    if tasks.empty:
        st.info("표시할 과제 데이터가 없습니다.")
        return

    bureau_options = ["전체"] + unique_values(tasks, "lead_bureau")
    selected_bureau = st.selectbox("국 선택", bureau_options)
    scoped = tasks if selected_bureau == "전체" else tasks[tasks["lead_bureau"] == selected_bureau]

    division_options = ["전체"] + unique_values(scoped, "lead_division")
    selected_division = st.selectbox("과 선택", division_options)
    if selected_division != "전체":
        scoped = scoped[scoped["lead_division"] == selected_division]

    metric_cols = st.columns(4)
    metric_cols[0].metric("조직 과제", f"{len(scoped):,}개")
    metric_cols[1].metric("평균 진척률", f"{scoped['progress'].mean():.0f}%" if not scoped.empty else "0%")
    metric_cols[2].metric("진행중", f"{(scoped['status'] == '진행중').sum():,}개")
    metric_cols[3].metric("상위험", f"{(scoped['risk_level'] == '상').sum():,}개")

    if not scoped.empty:
        division_counts = scoped.groupby(["lead_bureau", "lead_division"], as_index=False).size().rename(columns={"size": "과제 수"})
        st.plotly_chart(
            px.bar(division_counts, x="lead_division", y="과제 수", color="lead_bureau", text="과제 수", labels={"lead_division": "주관과"}),
            use_container_width=True,
        )

    organization_columns = columns_for_view(config, "organization")
    st.dataframe(label_dataframe(scoped, config, organization_columns), use_container_width=True, hide_index=True)


def main() -> None:
    config = load_config()
    eav_data = load_eav_data()
    tasks = materialize_tasks(config, eav_data)

    render_header(config)
    overview_tab, explorer_tab, organization_tab = st.tabs(["종합", "과제 탐색", "조직별"])
    with overview_tab:
        render_overview(config, tasks)
    with explorer_tab:
        render_task_explorer(config, tasks)
    with organization_tab:
        render_organization(config, tasks)


if __name__ == "__main__":
    main()

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).parent
MODEL_CONFIG_PATH = ROOT / "model_config.json"
SAMPLE_DATA_PATH = ROOT / "data" / "sample_ai_tasks.json"

st.set_page_config(
    page_title="지식재산처 AI과제 관리 대시보드",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600;700&display=swap');

    :root {
        --kai-bg: #0d1117;
        --kai-surface: #161b22;
        --kai-surface-2: #1c2333;
        --kai-border: #2d3748;
        --kai-text: #e2e8f0;
        --kai-muted: #8892a4;
        --kai-blue: #3b82f6;
        --kai-blue-light: #60a5fa;
        --kai-green: #10b981;
        --kai-yellow: #f59e0b;
        --kai-red: #ef4444;
        --kai-accent: #6366f1;
    }

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59,130,246,0.14), transparent 34rem),
            radial-gradient(circle at 80% 0%, rgba(99,102,241,0.16), transparent 28rem),
            var(--kai-bg);
        color: var(--kai-text);
    }

    .block-container {
        max-width: 1480px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    [data-testid="stHeader"] { background: rgba(13,17,23,0.86); backdrop-filter: blur(12px); }
    [data-testid="stSidebar"] { background: #0f1623; border-right: 1px solid var(--kai-border); }
    [data-testid="stSidebar"] * { color: var(--kai-text); }

    h1, h2, h3, h4, h5, h6, p, label, span, div { color: inherit; }
    h2, h3 { letter-spacing: -0.02em; }

    div[data-testid="stTabs"] button {
        border-radius: 8px;
        color: var(--kai-muted);
        padding: 0.35rem 1.15rem;
        transition: all 0.18s ease;
    }
    div[data-testid="stTabs"] button:hover {
        background: var(--kai-surface-2);
        color: var(--kai-text);
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        background: rgba(59,130,246,0.13);
        color: var(--kai-blue-light);
    }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: var(--kai-blue-light); }

    div[data-testid="stMetric"],
    div[data-testid="stExpander"],
    div[data-testid="stDataFrame"],
    div[data-testid="stPlotlyChart"] {
        background: rgba(22,27,34,0.92);
        border: 1px solid var(--kai-border);
        border-radius: 12px;
        box-shadow: 0 18px 42px rgba(0,0,0,0.18);
    }

    div[data-testid="stMetric"] {
        padding: 1.05rem 1rem;
    }
    div[data-testid="stMetricLabel"] p {
        color: var(--kai-muted);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] {
        color: var(--kai-blue-light);
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 700;
    }
    div[data-testid="stPlotlyChart"] { padding: 0.75rem; }
    div[data-testid="stDataFrame"] { overflow: hidden; }
    div[data-testid="stExpander"] details { border: none; }

    .kai-topbar {
        position: sticky;
        top: 0;
        z-index: 10;
        display: flex;
        align-items: center;
        gap: 1rem;
        min-height: 56px;
        margin: -0.35rem 0 1rem;
        padding: 0 1rem;
        background: rgba(13,17,23,0.92);
        backdrop-filter: blur(12px);
        border: 1px solid var(--kai-border);
        border-radius: 14px;
    }
    .kai-logo {
        color: var(--kai-accent);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.84rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        white-space: nowrap;
    }
    .kai-nav-pill {
        padding: 0.34rem 0.92rem;
        border-radius: 8px;
        background: rgba(59,130,246,0.12);
        color: var(--kai-blue-light);
        font-size: 0.82rem;
        font-weight: 600;
    }
    .kai-updated {
        margin-left: auto;
        color: var(--kai-muted);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        white-space: nowrap;
    }

    .kai-hero {
        margin-bottom: 1.05rem;
        padding: 1.35rem 1.5rem;
        border: 1px solid var(--kai-border);
        border-radius: 16px;
        background:
            linear-gradient(135deg, rgba(28,35,51,0.98), rgba(22,27,34,0.96)),
            radial-gradient(circle at 95% 10%, rgba(96,165,250,0.18), transparent 18rem);
        box-shadow: 0 24px 60px rgba(0,0,0,0.25);
    }
    .kai-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--kai-blue-light);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .kai-hero h1 {
        margin: 0.35rem 0 0.35rem;
        color: var(--kai-text);
        font-size: clamp(1.75rem, 3vw, 2.55rem);
        font-weight: 800;
        letter-spacing: -0.04em;
    }
    .kai-hero p {
        margin: 0;
        color: var(--kai-muted);
        font-size: 0.95rem;
    }

    .kai-section-title {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin: 0.35rem 0 1rem;
        color: var(--kai-text);
        font-size: 1.08rem;
        font-weight: 800;
    }
    .kai-section-title::before {
        content: '';
        width: 4px;
        height: 20px;
        border-radius: 999px;
        background: var(--kai-blue);
    }
    .small-muted { color: var(--kai-muted); font-size: 0.9rem; }
    .task-title { font-weight: 700; color: var(--kai-text); }
    .rec-box {
        border-left: 4px solid var(--kai-blue);
        padding: .75rem 1rem;
        background: var(--kai-surface);
        border-radius: 8px;
        margin-bottom: .6rem;
    }
    .schema-chip {
        display: inline-block;
        margin: .15rem .25rem .15rem 0;
        padding: .2rem .55rem;
        border: 1px solid rgba(59,130,246,0.35);
        border-radius: 999px;
        background: rgba(59,130,246,0.12);
        color: var(--kai-blue-light);
        font-size: .85rem;
    }
    .kai-card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 0.8rem;
        margin-bottom: 1rem;
    }
    .kai-metric-card {
        padding: 1rem;
        border: 1px solid var(--kai-border);
        border-radius: 12px;
        background: rgba(22,27,34,0.94);
        box-shadow: 0 18px 42px rgba(0,0,0,0.16);
    }
    .kai-metric-label {
        color: var(--kai-muted);
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
    }
    .kai-metric-value {
        margin-top: 0.35rem;
        color: var(--kai-blue-light);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.05;
    }
    .kai-metric-note {
        margin-top: 0.3rem;
        color: var(--kai-muted);
        font-size: 0.76rem;
    }
    .kai-project-card {
        padding: 1rem 1.1rem;
        border: 1px solid var(--kai-border);
        border-radius: 12px;
        background: rgba(22,27,34,0.93);
        transition: border-color 0.18s, background 0.18s;
    }
    .kai-project-card:hover {
        border-color: var(--kai-blue);
        background: rgba(28,35,51,0.98);
    }
    .kai-tag-row { display: flex; gap: 0.45rem; flex-wrap: wrap; margin-bottom: 0.7rem; }
    .kai-tag {
        padding: 0.18rem 0.5rem;
        border: 1px solid var(--kai-border);
        border-radius: 5px;
        background: var(--kai-surface-2);
        color: var(--kai-muted);
        font-size: 0.64rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .kai-project-title { color: var(--kai-text); font-size: 0.96rem; font-weight: 700; }
    .kai-project-desc { margin-top: 0.45rem; color: var(--kai-muted); font-size: 0.82rem; line-height: 1.5; }
    .kai-progress-track { height: 6px; margin-top: 0.8rem; background: var(--kai-bg); border-radius: 999px; overflow: hidden; }
    .kai-progress-fill { height: 100%; background: linear-gradient(90deg, var(--kai-green), var(--kai-blue)); border-radius: 999px; }
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
def load_sample_entities() -> list[dict[str, Any]]:
    with SAMPLE_DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(show_spinner=False)
def load_eav_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    """JSON 샘플 데이터를 EAV(Entity-Attribute-Value) 형태로 변환합니다.

    실제 저장소가 붙기 전까지 별도 JSON 파일의 임시 데이터를 사용하되,
    model_config.json의 필드명을 그대로 attribute로 사용해 화면 구조와 필터를 검증합니다.
    """
    configured_attributes = {
        entity_type: set(schema_fields(config, entity_type)) for entity_type in config.get("data_model", {})
    }

    rows: list[dict[str, Any]] = []
    for sample in load_sample_entities():
        entity_type = sample["entity_type"]
        values = sample.get("values", {})
        allowed_attributes = configured_attributes.get(entity_type, set())
        rows.extend(
            row
            for row in make_eav_entity(entity_type, sample["entity_id"], values)
            if row["attribute"] in allowed_attributes
        )
    return rows


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


def apply_chart_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Noto Sans KR", "color": "#e2e8f0"},
        legend={"font": {"color": "#8892a4"}},
        margin={"l": 16, "r": 16, "t": 24, "b": 16},
        colorway=["#60a5fa", "#10b981", "#f59e0b", "#6366f1", "#ef4444"],
    )
    fig.update_xaxes(gridcolor="#2d3748", zerolinecolor="#2d3748", tickfont={"color": "#8892a4"})
    fig.update_yaxes(gridcolor="#2d3748", zerolinecolor="#2d3748", tickfont={"color": "#8892a4"})
    return fig


def section_title(title: str) -> None:
    st.markdown(f"<div class='kai-section-title'>{html.escape(title)}</div>", unsafe_allow_html=True)


def metric_cards(cards: list[tuple[str, str, str]]) -> None:
    card_html = "".join(
        "<div class='kai-metric-card'>"
        f"<div class='kai-metric-label'>{html.escape(label)}</div>"
        f"<div class='kai-metric-value'>{html.escape(value)}</div>"
        f"<div class='kai-metric-note'>{html.escape(note)}</div>"
        "</div>"
        for label, value, note in cards
    )
    st.markdown(f"<div class='kai-card-grid'>{card_html}</div>", unsafe_allow_html=True)


def status_progress(status: Any) -> int:
    text = str(status or "")
    if "완료" in text:
        return 100
    if "진행" in text:
        return 75
    if "착수" in text:
        return 50
    if "선정" in text:
        return 25
    return 35


def render_project_card(record: dict[str, Any]) -> None:
    title = str(record.get("AI과제명") or record.get("내역사업명") or record.get("ID", ""))
    dept = " · ".join(str(record.get(key, "")) for key in ["부서(국)", "부서(과)"] if record.get(key))
    status = str(record.get("진행상태", "상태 미지정"))
    budget = record.get("사업비(백만원)", "")
    desc = str(record.get("과제설명", ""))
    progress = status_progress(status)
    st.markdown(
        "<div class='kai-project-card'>"
        "<div class='kai-tag-row'>"
        f"<span class='kai-tag'>{html.escape(str(record.get('ID', '')))}</span>"
        f"<span class='kai-tag'>{html.escape(status)}</span>"
        f"<span class='kai-tag'>{html.escape(str(budget))} 백만원</span>"
        "</div>"
        f"<div class='kai-project-title'>{html.escape(title)}</div>"
        f"<div class='kai-project-desc'>{html.escape(dept)}</div>"
        f"<div class='kai-project-desc'>{html.escape(desc[:120])}</div>"
        "<div class='kai-progress-track'>"
        f"<div class='kai-progress-fill' style='width:{progress}%;'></div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def render_header(biz_df: pd.DataFrame, budget_df: pd.DataFrame) -> None:
    total_budget = normalize_money(biz_df.get("사업비(백만원)", pd.Series(dtype="float64"))).sum()
    next_budget = normalize_money(budget_df.get("사업비(백만원)", pd.Series(dtype="float64"))).sum()
    completed = int(biz_df.get("진행상태", pd.Series(dtype="object")).astype(str).str.contains("완료", na=False).sum())

    st.markdown(
        "<div class='kai-topbar'>"
        "<div class='kai-logo'>AI·BMS</div>"
        "<div class='kai-nav-pill'>📊 대시보드</div>"
        "<div class='kai-nav-pill'>📁 과제 탐색</div>"
        "<div class='kai-nav-pill'>🏢 조직별</div>"
        "<div class='kai-updated'>STREAMLIT · EAV SAMPLE</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<section class='kai-hero'>"
        "<div class='kai-eyebrow'>KIPO AI PROJECT CONTROL CENTER</div>"
        "<h1>지식재산처 AI과제 관리 대시보드</h1>"
        "<p>model_config.json 기반 EAV 임시 데이터는 유지하되, HTML 시안의 다크 톤·카드·상단 내비게이션 시각 요소를 Streamlit 화면에 적용했습니다.</p>"
        "</section>",
        unsafe_allow_html=True,
    )
    metric_cards(
        [
            ("AI과제", f"{len(biz_df):,}개", "현재 관리 중인 사업 데이터"),
            ("완료 과제", f"{completed:,}개", "진행상태 기준"),
            ("26년 예산", f"{total_budget:,.0f}", "백만원"),
            ("27년 예산안", f"{len(budget_df):,}건", "예산안 항목 수"),
            ("27년 예산안", f"{next_budget:,.0f}", "백만원"),
            ("총 사업비", f"{total_budget:,.0f}", "백만원"),
        ]
    )



def render_schema_note(config: dict[str, Any], entity_type: str) -> None:
    fields = schema_fields(config, entity_type)
    chips = "".join(f"<span class='schema-chip'>{field}</span>" for field in fields)
    st.markdown(f"**{entity_type} 표시 필드(model_config.json 기준)**  ")
    st.markdown(chips, unsafe_allow_html=True)


def render_overview(config: dict[str, Any], biz_df: pd.DataFrame, budget_df: pd.DataFrame) -> None:
    section_title("종합 현황")
    # render_schema_note(config, "사업")

    left, right = st.columns([1, 1])
    with left:
        status_counts = biz_df.groupby("진행상태", dropna=False, as_index=False).size().rename(columns={"size": "과제 수"})
        status_fig = px.pie(status_counts, values="과제 수", names="진행상태", hole=0.45)
        status_fig.update_traces(textfont_color="#e2e8f0", marker={"line": {"color": "#161b22", "width": 2}})
        st.plotly_chart(apply_chart_theme(status_fig), use_container_width=True)
    with right:
        guk_counts = biz_df.groupby("부서(국)", dropna=False, as_index=False).size().rename(columns={"size": "과제 수"}).sort_values("과제 수")
        guk_fig = px.bar(guk_counts, x="과제 수", y="부서(국)", orientation="h", text="과제 수")
        guk_fig.update_traces(marker_color="#60a5fa", textfont_color="#e2e8f0")
        st.plotly_chart(apply_chart_theme(guk_fig), use_container_width=True)

    budget_by_guk = biz_df.assign(**{"사업비(백만원)": normalize_money(biz_df["사업비(백만원)"])}).groupby("부서(국)", as_index=False)["사업비(백만원)"].sum()
    section_title("국별 사업비(백만원)")
    budget_fig = px.bar(
        budget_by_guk.sort_values("사업비(백만원)", ascending=False),
        x="부서(국)",
        y="사업비(백만원)",
        text="사업비(백만원)",
    )
    budget_fig.update_traces(marker_color="#10b981", textfont_color="#e2e8f0")
    st.plotly_chart(apply_chart_theme(budget_fig), use_container_width=True)

    section_title("AI과제 목록")
    st.dataframe(biz_df, use_container_width=True, hide_index=True)

    section_title("27년 예산안")
    # render_schema_note(config, "27년 예산안")
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
    section_title("과제 탐색")
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
    # render_schema_note(config, entity_type)
    st.caption(f"검색 결과: {len(filtered):,}건")

    preview_records = filtered.head(4).to_dict("records")
    if preview_records:
        preview_cols = st.columns(min(4, len(preview_records)))
        for column, record in zip(preview_cols, preview_records):
            with column:
                render_project_card(record)

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
            detail["값"] = detail["값"].astype(str)
            st.dataframe(detail, use_container_width=True, hide_index=True)



def render_organizations(organizations: dict[str, list[str]], biz_df: pd.DataFrame, budget_df: pd.DataFrame) -> None:
    section_title("조직별 실행 현황")
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
    metric_cards(
        [
            ("관리 항목", f"{len(filtered):,}건", selected_guk),
            ("사업비", f"{budget_sum:,.0f}", "백만원"),
            ("소속 과", f"{len(gwa_options):,}개", selected_gwa),
        ]
    )

    if filtered.empty:
        st.info("선택한 조직에 연결된 임시 과제가 없습니다.")
        return

    by_gwa = filtered.groupby(["부서(과)", "구분"], dropna=False, as_index=False).size().rename(columns={"size": "건수"})
    org_fig = px.bar(by_gwa, x="부서(과)", y="건수", color="구분", text="건수", barmode="group")
    org_fig.update_traces(textfont_color="#e2e8f0")
    st.plotly_chart(apply_chart_theme(org_fig), use_container_width=True)
    st.dataframe(filtered, use_container_width=True, hide_index=True)



def render_eav_debug(eav_rows: list[dict[str, Any]]) -> None:
    with st.expander("EAV 원천 행 보기"):
        st.caption("entity_type, entity_id, attribute, value 구조로 임시 구성한 데이터입니다.")
        df = pd.DataFrame(eav_rows)
        df["value"] = df["value"].astype(str)
        st.dataframe(df, use_container_width=True, hide_index=True)


def main() -> None:
    config = load_model_config()
    organizations = config.get("organizations", {})
    eav_rows = load_eav_rows(config)
    biz_df = eav_to_records(eav_rows, config, "사업")
    budget_df = eav_to_records(eav_rows, config, "27년 예산안")

    render_header(biz_df, budget_df)

    tab_names = ["종합", "과제 탐색", "조직별"]
    tabs = st.tabs(tab_names)
    with tabs[0]:
        render_overview(config, biz_df, budget_df)
        # render_eav_debug(eav_rows)
    with tabs[1]:
        render_tasks(config, biz_df, budget_df)
    with tabs[2]:
        render_organizations(organizations, biz_df, budget_df)


if __name__ == "__main__":
    main()
    
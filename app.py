from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
EVAL_DIR = DATA_DIR / "task_eval"

st.set_page_config(
    page_title="대한민국 AI 행동계획 2026 대시보드",
    page_icon="🇰🇷",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    .metric-card {background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 14px; padding: 1rem;}
    .small-muted {color:#64748b; font-size:0.9rem;}
    .task-title {font-weight:700; color:#0f172a;}
    .rec-box {border-left: 4px solid #2563eb; padding: .75rem 1rem; background:#f8fafc; border-radius: 8px; margin-bottom:.6rem;}
    .danger-box {border-left: 4px solid #dc2626; padding: .75rem 1rem; background:#fff7f7; border-radius: 8px; margin-bottom:.6rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_json(relative_path: str) -> Any:
    with (ROOT / relative_path).open(encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(show_spinner=False)
def load_core_data() -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    tasks_payload = load_json("data/tasks.json")
    ministries_payload = load_json("data/ministries.json")
    references_payload = load_json("data/references.json")
    timeline_payload = load_json("data/timeline.json")
    global_payload = load_json("data/globalai_cases.json")
    return (
        tasks_payload["tasks"],
        tasks_payload.get("meta", {}),
        ministries_payload.get("ministries", []),
        references_payload,
        {"timeline": timeline_payload, "global": global_payload},
    )


@st.cache_data(show_spinner=False)
def build_recommendation_frame(tasks: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for task in tasks:
        for recommendation in task.get("recommendations", []):
            rows.append(
                {
                    "task_id": task["id"],
                    "task_title": task["title"],
                    "policy_axis": task["policy_axis_name"],
                    "strategic_area": task["strategic_area_name"],
                    "ministry": recommendation.get("ministry", "미지정"),
                    "deadline": recommendation.get("deadline", ""),
                    "deadline_label": recommendation.get("deadline_label", ""),
                    "status": recommendation.get("status", ""),
                    "content": recommendation.get("content", ""),
                }
            )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def load_eval_index() -> dict[int, dict[str, Path]]:
    index: dict[int, dict[str, Path]] = defaultdict(dict)
    for path in EVAL_DIR.glob("task_*_*.json"):
        parts = path.stem.split("_")
        if len(parts) >= 3 and parts[1].isdigit():
            index[int(parts[1])][parts[2]] = path
    return dict(index)


def filter_tasks(
    tasks: list[dict[str, Any]],
    query: str,
    axes: list[str],
    areas: list[str],
    ministries: list[str],
) -> list[dict[str, Any]]:
    q = query.strip().lower()
    filtered: list[dict[str, Any]] = []
    for task in tasks:
        recs = task.get("recommendations", [])
        searchable = " ".join(
            [task.get("title", ""), task.get("background", "")]
            + [rec.get("content", "") + " " + rec.get("ministry", "") for rec in recs]
        ).lower()
        task_ministries = {rec.get("ministry", "미지정") for rec in recs}
        if q and q not in searchable:
            continue
        if axes and task.get("policy_axis_name") not in axes:
            continue
        if areas and task.get("strategic_area_name") not in areas:
            continue
        if ministries and not task_ministries.intersection(ministries):
            continue
        filtered.append(task)
    return filtered


def short_text(text: str, limit: int = 180) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def render_header(meta: dict[str, Any]) -> None:
    st.title("🇰🇷 대한민국 AI 행동계획 2026 대시보드")
    st.caption("대통령직속 국가인공지능전략위원회 99개 실천과제 / 326개 정책권고 데이터를 Streamlit으로 탐색합니다. (비공식)")
    cols = st.columns(4)
    cols[0].metric("실천과제", f"{meta.get('total_tasks', 99):,}개")
    cols[1].metric("정책권고", f"{meta.get('total_recommendations', 326):,}개")
    cols[2].metric("정책축", f"{meta.get('policy_axes', 3):,}개")
    cols[3].metric("전략분야", f"{meta.get('strategic_areas', 12):,}개")


def render_overview(tasks: list[dict[str, Any]], rec_df: pd.DataFrame, ministries_data: list[dict[str, Any]]) -> None:
    st.subheader("종합 현황")
    axis_counts = pd.DataFrame(Counter(task["policy_axis_name"] for task in tasks).items(), columns=["정책축", "과제 수"])
    area_counts = pd.DataFrame(Counter(task["strategic_area_name"] for task in tasks).items(), columns=["전략분야", "과제 수"])
    ministry_counts = rec_df.groupby("ministry", as_index=False).size().rename(columns={"size": "권고 수"}).sort_values("권고 수", ascending=False)

    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(px.pie(axis_counts, values="과제 수", names="정책축", hole=0.45), use_container_width=True)
    with right:
        st.plotly_chart(px.bar(area_counts, x="과제 수", y="전략분야", orientation="h", text="과제 수"), use_container_width=True)

    st.markdown("#### 담당 부처별 권고 수 Top 15")
    st.plotly_chart(px.bar(ministry_counts.head(15), x="ministry", y="권고 수", text="권고 수"), use_container_width=True)

    urgent_rows = []
    for ministry in ministries_data:
        for action in ministry.get("actions", []):
            if action.get("is_urgent") or action.get("is_overdue"):
                urgent_rows.append({"부처": ministry["name"], "과제": action["task_title"], "기한": action["deadline_label"], "내용": short_text(action["content"], 120)})
    if urgent_rows:
        st.markdown("#### 임박/주의 권고")
        st.dataframe(pd.DataFrame(urgent_rows), use_container_width=True, hide_index=True)


def render_tasks(tasks: list[dict[str, Any]], rec_df: pd.DataFrame) -> None:
    st.subheader("실천과제 탐색")
    axes = sorted({task["policy_axis_name"] for task in tasks})
    areas = sorted({task["strategic_area_name"] for task in tasks})
    ministries = sorted(set(rec_df["ministry"].dropna()))
    with st.sidebar:
        st.markdown("### 필터")
        query = st.text_input("검색어", placeholder="예: GPU, 안전, 교육, 과기정통부")
        selected_axes = st.multiselect("정책축", axes)
        selected_areas = st.multiselect("전략분야", areas)
        selected_ministries = st.multiselect("담당 부처", ministries)

    filtered = filter_tasks(tasks, query, selected_axes, selected_areas, selected_ministries)
    st.caption(f"검색 결과: {len(filtered):,}개 과제")
    for task in filtered:
        with st.expander(f"[{task['id']}] {task['title']} — {task['strategic_area_name']}"):
            st.markdown(f"**정책축:** {task['policy_axis_name']}  \n**전략분야:** {task['strategic_area_name']}")
            st.markdown("**배경**")
            st.write(task.get("background", ""))
            st.markdown("**정책권고**")
            for rec in task.get("recommendations", []):
                st.markdown(
                    f"<div class='rec-box'><b>{rec.get('seq')}. {rec.get('ministry')}</b> · {rec.get('deadline_label', rec.get('deadline', ''))} · {rec.get('status', '')}<br>{rec.get('content', '')}</div>",
                    unsafe_allow_html=True,
                )


def render_ministries(ministries_data: list[dict[str, Any]]) -> None:
    st.subheader("부처별 실행 현황")
    names = [f"{m['name']} ({m.get('recommendation_count', len(m.get('actions', [])))})" for m in ministries_data]
    choice = st.selectbox("부처 선택", names)
    ministry = ministries_data[names.index(choice)]
    st.metric(ministry.get("full_name", ministry["name"]), f"{ministry.get('recommendation_count', len(ministry.get('actions', []))):,}개 권고")
    rows = [
        {
            "과제 ID": action["task_id"],
            "과제명": action["task_title"],
            "기한": action.get("deadline_label", action.get("deadline", "")),
            "상태": action.get("status", ""),
            "임박": "예" if action.get("is_urgent") else "",
            "내용": action.get("content", ""),
        }
        for action in ministry.get("actions", [])
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_timeline(timeline_payload: dict[str, Any]) -> None:
    st.subheader("이행 일정")
    quarters = timeline_payload.get("quarters", [])
    if quarters:
        quarter_df = pd.DataFrame(quarters)
        st.plotly_chart(px.bar(quarter_df, x="label", y="count", text="count", labels={"label": "분기", "count": "권고 수"}), use_container_width=True)
        st.dataframe(quarter_df.rename(columns={"id": "분기 ID", "label": "분기", "count": "권고 수", "pct": "비중(%)"}), use_container_width=True, hide_index=True)

    quarter_details = timeline_payload.get("quarter_details", {})
    if isinstance(quarter_details, dict) and quarter_details:
        detail_df = pd.DataFrame([{"분기 ID": quarter, "권고 수": count} for quarter, count in quarter_details.items()])
        with st.expander("원본 분기별 집계 보기"):
            st.dataframe(detail_df, use_container_width=True, hide_index=True)

    parsed = timeline_payload.get("parsed_summary", {})
    if parsed:
        summary_rows = [{"구간": key, **value} for key, value in parsed.items() if isinstance(value, dict)]
        if summary_rows:
            st.markdown("#### 기간 구간 요약")
            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)


def render_global_cases(global_payload: dict[str, Any]) -> None:
    st.subheader("글로벌 AI 정책 사례")
    cases = global_payload.get("cases", [])
    if not cases:
        st.info("사례 데이터가 없습니다.")
        return
    countries = sorted({case.get("country", "") for case in cases if case.get("country")})
    categories = sorted({case.get("category", "") for case in cases if case.get("category")})
    col1, col2 = st.columns(2)
    country = col1.multiselect("국가", countries)
    category = col2.multiselect("분류", categories)
    filtered = [case for case in cases if (not country or case.get("country") in country) and (not category or case.get("category") in category)]
    st.caption(f"{len(filtered):,}개 사례")
    for case in filtered:
        with st.expander(f"{case.get('country')} · {case.get('category')} · {case.get('title')}"):
            st.write(case.get("summary", ""))
            st.write("키워드:", ", ".join(case.get("keywords", [])))
            st.caption(case.get("date", ""))


def render_references(references_payload: dict[str, Any]) -> None:
    st.subheader("참고자료 / 각주 검색")
    query = st.text_input("참고자료 검색", placeholder="검색어를 입력하세요")
    q = query.lower().strip()
    refs = references_payload.get("references", [])
    footnotes = references_payload.get("footnotes", [])
    for title, items in [("참고자료", refs), ("각주", footnotes)]:
        st.markdown(f"#### {title}")
        matched = [item for item in items if not q or q in json.dumps(item, ensure_ascii=False).lower()]
        st.caption(f"{len(matched):,}건")
        st.dataframe(pd.DataFrame(matched), use_container_width=True, hide_index=True)


def render_eval(tasks: list[dict[str, Any]]) -> None:
    st.subheader("AI 페르소나 평가")
    eval_index = load_eval_index()
    available_ids = sorted(eval_index)
    task_options = {f"[{task['id']}] {task['title']}": task["id"] for task in tasks if task["id"] in eval_index}
    if not task_options:
        st.info("평가 데이터가 없습니다.")
        return
    selected_label = st.selectbox("평가 과제", list(task_options))
    task_id = task_options[selected_label]
    labels = {"success": "성공/실패 예측", "risk": "리스크 분석", "cooperation": "협력 분석"}
    available_types = list(eval_index.get(task_id, {}))
    selected_type = st.radio("분석 유형", available_types, format_func=lambda key: labels.get(key, key), horizontal=True)
    with eval_index[task_id][selected_type].open(encoding="utf-8") as file:
        payload = json.load(file)
    st.caption(f"모델: {payload.get('model', '')} · 생성: {payload.get('generated_at', '')}")
    for result in payload.get("results", []):
        with st.expander(result.get("persona_name", result.get("persona", "페르소나"))):
            st.markdown(result.get("response", ""))


def render_sankey(tasks: list[dict[str, Any]], rec_df: pd.DataFrame) -> None:
    st.subheader("정책축 → 전략분야 → 과제 → 부처 흐름")
    max_tasks = st.slider("표시할 과제 수", 10, len(tasks), min(40, len(tasks)), step=5)
    selected_tasks = tasks[:max_tasks]
    labels: list[str] = []
    index: dict[str, int] = {}
    sources: list[int] = []
    targets: list[int] = []
    values: list[int] = []

    def node(label: str) -> int:
        if label not in index:
            index[label] = len(labels)
            labels.append(label)
        return index[label]

    for task in selected_tasks:
        axis = node("축: " + task["policy_axis_name"])
        area = node("분야: " + task["strategic_area_name"])
        task_node = node(f"[{task['id']}] {short_text(task['title'], 28)}")
        sources.extend([axis, area])
        targets.extend([area, task_node])
        values.extend([1, 1])
        for ministry in {rec.get("ministry", "미지정") for rec in task.get("recommendations", [])}:
            sources.append(task_node)
            targets.append(node("부처: " + ministry))
            values.append(1)

    fig = go.Figure(data=[go.Sankey(node={"label": labels, "pad": 12, "thickness": 14}, link={"source": sources, "target": targets, "value": values})])
    fig.update_layout(height=850, font_size=11)
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    tasks, meta, ministries_data, references_payload, extra = load_core_data()
    rec_df = build_recommendation_frame(tasks)
    render_header(meta)

    tab_names = ["종합", "과제 탐색", "부처별", "일정", "흐름도", "글로벌 사례", "참고자료", "AI 평가"]
    tabs = st.tabs(tab_names)
    with tabs[0]:
        render_overview(tasks, rec_df, ministries_data)
    with tabs[1]:
        render_tasks(tasks, rec_df)
    with tabs[2]:
        render_ministries(ministries_data)
    with tabs[3]:
        render_timeline(extra["timeline"])
    with tabs[4]:
        render_sankey(tasks, rec_df)
    with tabs[5]:
        render_global_cases(extra["global"])
    with tabs[6]:
        render_references(references_payload)
    with tabs[7]:
        render_eval(tasks)


if __name__ == "__main__":
    main()

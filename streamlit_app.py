from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# -----------------------------------------------------------------------------
# SupeRR Selector Season 2 | Interactive pressure-performance dashboard
# This app displays the precomputed outputs of analyze_cricket.py and
# finalize_deliverables.py. It does not rerun the ball-by-ball modelling.
# -----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
REPORT_PATH = ASSETS / "SupeRR_Selector_Season2_Analysis_Report.pdf"

st.set_page_config(
    page_title="SupeRR Selector | Pressure Performance Lab",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Visual system
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
      html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
      .stApp { background: #0a1020; color: #eef3ff; }
      [data-testid="stHeader"] { background: rgba(10,16,32,0.92); }
      [data-testid="stSidebar"] { background: #101a2e; border-right: 1px solid #24314a; }
      [data-testid="stSidebar"] * { color: #eaf0ff; }
      .block-container { padding-top: 1.4rem; padding-bottom: 2.5rem; max-width: 1500px; }
      h1, h2, h3 { font-family: 'Manrope', sans-serif !important; letter-spacing: -0.035em; }
      h1 { color: #f5f7ff; font-weight: 800 !important; }
      h2, h3 { color: #edf2ff; }
      p, label, .stMarkdown { color: #c5cee0; }
      .hero { padding: 1.4rem 1.6rem; border: 1px solid #293a59; border-radius: 18px;
              background: linear-gradient(120deg, #14213a 0%, #101a2e 60%, #162642 100%); }
      .eyebrow { color: #55d6be; text-transform: uppercase; letter-spacing: .16em; font-size: .72rem; font-weight: 800; }
      .hero-title { font-family: 'Manrope',sans-serif; color: #fff; font-size: clamp(1.9rem, 4vw, 3rem); font-weight: 800; line-height: 1.06; margin: .5rem 0 .65rem; }
      .hero-sub { color: #bac8df; max-width: 850px; font-size: 1rem; }
      .metric-card { background: #121e33; border: 1px solid #283854; border-radius: 15px; padding: 1rem 1.1rem; min-height: 108px; }
      .metric-label { color: #91a2bf; font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 700; }
      .metric-value { color: #ffffff; font-family: 'Manrope',sans-serif; font-size: 1.9rem; font-weight: 800; line-height: 1.25; margin-top: .25rem; }
      .metric-help { color: #91a2bf; font-size: .75rem; margin-top: .15rem; }
      .section-kicker { color: #55d6be; font-size: .72rem; font-weight: 800; letter-spacing: .15em; text-transform: uppercase; }
      .note { border-left: 3px solid #55d6be; background: #12223a; padding: .85rem 1rem; border-radius: 0 10px 10px 0; color: #c6d3e7; }
      .small-muted { color: #8fa1bf; font-size: .82rem; }
      div[data-testid="stDataFrame"] { border: 1px solid #283854; border-radius: 12px; overflow: hidden; }
      .stButton button, .stDownloadButton button { border-radius: 10px; font-weight: 700; }
      button[kind="primary"] { background: #23b89f !important; border-color: #23b89f !important; color: #071723 !important; }
      .stTabs [data-baseweb="tab-list"] { gap: .4rem; }
      .stTabs [data-baseweb="tab"] { background: #121e33; border: 1px solid #283854; border-radius: 10px 10px 0 0; padding: .55rem 1rem; }
      .stTabs [aria-selected="true"] { background: #1d3850 !important; border-bottom: 2px solid #55d6be !important; }
      hr { border-color: #263550; }
      a { color: #55d6be !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_csv(filename: str) -> pd.DataFrame:
    path = DATA / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_json(filename: str) -> dict[str, Any]:
    path = DATA / filename
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fmt_int(value: Any) -> str:
    try:
        if pd.isna(value):
            return "—"
        return f"{int(round(float(value))):,}"
    except (TypeError, ValueError):
        return "—"


def fmt_num(value: Any, digits: int = 1) -> str:
    try:
        if pd.isna(value):
            return "—"
        return f"{float(value):,.{digits}f}"
    except (TypeError, ValueError):
        return "—"


def metric_card(label: str, value: str, help_text: str = "") -> None:
    st.markdown(
        f"<div class='metric-card'><div class='metric-label'>{label}</div>"
        f"<div class='metric-value'>{value}</div><div class='metric-help'>{help_text}</div></div>",
        unsafe_allow_html=True,
    )


def chart_layout(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        height=height,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#dbe5f5", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.2),
        hoverlabel=dict(bgcolor="#172740", font_color="#ffffff"),
    )
    fig.update_xaxes(gridcolor="#263550", zerolinecolor="#263550")
    fig.update_yaxes(gridcolor="#263550", zerolinecolor="#263550")
    return fig


def safe_download(df: pd.DataFrame, label: str, filename: str, key: str) -> None:
    if not df.empty:
        st.download_button(
            label=label,
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=filename,
            mime="text/csv",
            key=key,
        )


# Load the derived results
bat_top = load_csv("Top_10_Batters.csv")
bowl_top = load_csv("Top_10_Bowlers.csv")
complete = load_csv("Complete_Player_Leaderboard.csv")
bat_all = load_csv("Batter_Leaderboard_All.csv")
bowl_all = load_csv("Bowler_Leaderboard_All.csv")
bat_comp = load_csv("IPL_T20I_Batter_Comparison.csv")
bowl_comp = load_csv("IPL_T20I_Bowler_Comparison.csv")
pressure_perf = load_csv("Pressure_Category_Performance.csv")
pressure_dist = load_csv("Pressure_Index_Distribution.csv")
phase_dist = load_csv("Pressure_Phase_Distribution.csv")
sensitivity = load_csv("Sensitivity_Analysis.csv")
weight_sensitivity = load_csv("Weight_Sensitivity.csv")
match_bat = load_csv("Match_Level_Batting_Pressure.csv")
match_bowl = load_csv("Match_Level_Bowling_Pressure.csv")
audit = load_json("Data_Audit.json")
detailed_audit = load_json("Data_Audit_Detailed.json")

if complete.empty or bat_top.empty or bowl_top.empty:
    st.error("Dashboard data files are missing. Keep the `data` folder beside `streamlit_app.py`.")
    st.stop()

# Sidebar
st.sidebar.markdown("<div class='eyebrow'>SupeRR Selector · Season 2</div>", unsafe_allow_html=True)
st.sidebar.title("Pressure Lab")
st.sidebar.caption("IPL + T20I · 2022 onwards")
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Top 10 Batters", "Top 10 Bowlers", "Player Explorer", "IPL vs T20I", "Model & Data Audit"],
    label_visibility="collapsed",
)
st.sidebar.divider()
st.sidebar.markdown("**Model reference**")
st.sidebar.caption("High pressure: Pressure Index ≥ 60\n\nExtreme pressure: Pressure Index ≥ 80")
st.sidebar.caption("Ratings are composite scores, not probabilities.")

# Header
st.markdown(
    "<div class='hero'><div class='eyebrow'>Data-led cricket intelligence</div>"
    "<div class='hero-title'>Who delivers when the game gets tight?</div>"
    "<div class='hero-sub'>Explore pressure-state performance across IPL and T20 Internationals. "
    "Compare players against their own baselines, inspect role-specific rankings, and review the evidence behind each rating.</div></div>",
    unsafe_allow_html=True,
)
st.write("")

if page == "Overview":
    st.markdown("<div class='section-kicker'>Competition snapshot</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: metric_card("Matches analysed", fmt_int(audit.get("matches_in_analysis_scope_metadata")), "Completed IPL + T20I matches")
    with c2: metric_card("Regulation deliveries", fmt_int(audit.get("regulation_delivery_rows")), "Ball-by-ball records")
    with c3: metric_card("High-pressure balls", fmt_int(audit.get("pressure_deliveries_ge60")), f"{100*audit.get('pressure_share_ge60',0):.2f}% of analysed deliveries")
    with c4: metric_card("Extreme-pressure balls", fmt_int(audit.get("extreme_deliveries_ge80")), f"{100*audit.get('extreme_share_ge80',0):.2f}% of analysed deliveries")
    with c5: metric_card("Eligible players", fmt_int(len(complete)), "54 batters · 163 bowlers")

    st.write("")
    left, right = st.columns([1.05, 1])
    with left:
        st.subheader("Pressure distribution")
        if not pressure_dist.empty:
            order = ["Low", "Moderate", "High", "Extreme"]
            d = pressure_dist.set_index("pressure_category").reindex(order).reset_index()
            fig = px.bar(d, x="pressure_category", y="deliveries", text="deliveries",
                         category_orders={"pressure_category": order},
                         color="pressure_category",
                         color_discrete_map={"Low":"#53718e", "Moderate":"#e3b45a", "High":"#ed875c", "Extreme":"#d95d78"})
            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig.update_layout(showlegend=False, yaxis_title="Deliveries", xaxis_title="")
            st.plotly_chart(chart_layout(fig, 330), use_container_width=True)
    with right:
        st.subheader("How performance changes with pressure")
        if not pressure_perf.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=pressure_perf["pressure_category"], y=pressure_perf["batting_strike_rate"],
                                     name="Batting strike rate", mode="lines+markers+text",
                                     line=dict(color="#55d6be", width=3), text=[f"{v:.1f}" for v in pressure_perf["batting_strike_rate"]], textposition="top center"))
            fig.add_trace(go.Scatter(x=pressure_perf["pressure_category"], y=pressure_perf["bowling_economy"],
                                     name="Bowling economy", mode="lines+markers+text",
                                     line=dict(color="#f1b65c", width=3), text=[f"{v:.1f}" for v in pressure_perf["bowling_economy"]], textposition="bottom center"))
            fig.update_layout(xaxis_title="Pressure category", yaxis_title="Rate", hovermode="x unified")
            st.plotly_chart(chart_layout(fig, 330), use_container_width=True)
            st.caption("Batting strike rate and bowling economy are different measures; read their axes as separate rate indicators.")

    st.write("")
    st.subheader("Current model leaders")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Batting · Pressure Batting Rating**")
        show = bat_top[["rank", "player_name", "pressure_batting_rating", "pressure_strike_rate", "pressure_balls_faced"]].head(5).copy()
        show.columns = ["Rank", "Player", "PBR", "Pressure SR", "Pressure balls"]
        st.dataframe(show, hide_index=True, use_container_width=True)
    with c2:
        st.markdown("**Bowling · Pressure Bowling Rating**")
        show = bowl_top[["rank", "player_name", "pressure_bowling_rating", "pressure_economy", "pressure_wickets", "pressure_legal_balls"]].head(5).copy()
        show.columns = ["Rank", "Player", "PBoR", "Pressure Econ", "Wickets", "Legal balls"]
        st.dataframe(show, hide_index=True, use_container_width=True)

    st.markdown("<div class='note'><b>Interpretation:</b> The Pressure Index captures observable match-state difficulty and leverage. It does not measure a player's psychological state. Composite ratings are relative to this dataset and model design, not probabilities of success.</div>", unsafe_allow_html=True)

elif page == "Top 10 Batters":
    st.markdown("<div class='section-kicker'>Pressure Batting Rating · PBR</div>", unsafe_allow_html=True)
    st.title("Top 10 batters under pressure")
    st.caption("Ranked from the precomputed primary rating. Pressure SR is shown alongside each player's low-pressure baseline.")
    metric_cols = st.columns(3)
    with metric_cols[0]: metric_card("Top-ranked batter", str(bat_top.iloc[0]["player_name"]), f"PBR {float(bat_top.iloc[0]['pressure_batting_rating']):.2f}")
    with metric_cols[1]: metric_card("Highest pressure SR", str(bat_top.loc[bat_top.pressure_strike_rate.idxmax(), "player_name"]), f"{bat_top.pressure_strike_rate.max():.1f} SR")
    with metric_cols[2]: metric_card("Largest pressure sample", str(bat_top.loc[bat_top.pressure_balls_faced.idxmax(), "player_name"]), f"{fmt_int(bat_top.pressure_balls_faced.max())} balls")

    fig = px.bar(bat_top.sort_values("pressure_batting_rating"), x="pressure_batting_rating", y="player_name", orientation="h",
                 color="pressure_batting_rating", color_continuous_scale=["#37516e", "#23b89f", "#b8eedf"],
                 hover_data={"pressure_strike_rate":":.1f", "normal_strike_rate":":.1f", "pressure_balls_faced":True, "matches_with_pressure_exposure":True})
    fig.update_layout(xaxis_title="Pressure Batting Rating", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(chart_layout(fig, 430), use_container_width=True)

    st.subheader("Ranking table")
    display = bat_top[["rank", "player_name", "player_id", "pressure_batting_rating", "pressure_strike_rate", "normal_strike_rate", "raw_pressure_minus_normal_sr", "pressure_balls_faced", "matches_with_pressure_exposure", "consistency_rate", "consistency_evidence", "ipl_rating", "t20i_rating"]].copy()
    display.columns = ["Rank", "Batter", "Player ID", "PBR", "Pressure SR", "Normal SR", "SR Δ", "Pressure balls", "Pressure matches", "Consistency", "Consistency evidence", "IPL rating", "T20I rating"]
    st.dataframe(display, hide_index=True, use_container_width=True, column_config={
        "PBR": st.column_config.NumberColumn(format="%.2f"),
        "Pressure SR": st.column_config.NumberColumn(format="%.1f"),
        "Normal SR": st.column_config.NumberColumn(format="%.1f"),
        "SR Δ": st.column_config.NumberColumn(format="%+.1f"),
        "Consistency": st.column_config.NumberColumn(format="%.0f%%"),
    })
    safe_download(bat_top, "Download Top 10 batters CSV", "Top_10_Batters.csv", "dl_bat_top")

    st.subheader("Inspect an individual batter")
    chosen = st.selectbox("Select batter", bat_top["player_name"].tolist(), key="batter_detail")
    row = bat_top.loc[bat_top.player_name == chosen].iloc[0]
    a, b, c, d = st.columns(4)
    with a: metric_card("Pressure strike rate", fmt_num(row.pressure_strike_rate), "Runs per 100 balls")
    with b: metric_card("Normal strike rate", fmt_num(row.normal_strike_rate), "Low-pressure baseline")
    with c: metric_card("Pressure exposure", fmt_int(row.pressure_balls_faced), "Balls faced")
    with d: metric_card("Extreme-pressure SR", fmt_num(row.extreme_pressure_strike_rate), f"{fmt_int(row.extreme_pressure_balls_faced)} balls")
    st.markdown(f"**Why this ranking?** {row.main_reason}")
    st.caption(f"90% match-bootstrap interval for pressure SR: {fmt_num(row.pressure_sr_90ci_low)}–{fmt_num(row.pressure_sr_90ci_high)}. Consistency evidence: {row.consistency_evidence}.")

elif page == "Top 10 Bowlers":
    st.markdown("<div class='section-kicker'>Pressure Bowling Rating · PBoR</div>", unsafe_allow_html=True)
    st.title("Top 10 bowlers under pressure")
    st.caption("Lower economy is better. The composite rating also incorporates context-matched performance, wickets, dot balls, consistency and exposure.")
    metric_cols = st.columns(3)
    with metric_cols[0]: metric_card("Top-ranked bowler", str(bowl_top.iloc[0]["player_name"]), f"PBoR {float(bowl_top.iloc[0]['pressure_bowling_rating']):.2f}")
    with metric_cols[1]: metric_card("Most pressure wickets", str(bowl_top.loc[bowl_top.pressure_wickets.idxmax(), "player_name"]), f"{fmt_int(bowl_top.pressure_wickets.max())} wickets")
    with metric_cols[2]: metric_card("Largest pressure sample", str(bowl_top.loc[bowl_top.pressure_legal_balls.idxmax(), "player_name"]), f"{fmt_int(bowl_top.pressure_legal_balls.max())} legal balls")

    fig = px.bar(bowl_top.sort_values("pressure_bowling_rating"), x="pressure_bowling_rating", y="player_name", orientation="h",
                 color="pressure_bowling_rating", color_continuous_scale=["#37516e", "#e7a74e", "#f3d99b"],
                 hover_data={"pressure_economy":":.2f", "normal_economy":":.2f", "pressure_wickets":True, "pressure_legal_balls":True})
    fig.update_layout(xaxis_title="Pressure Bowling Rating", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(chart_layout(fig, 430), use_container_width=True)

    st.subheader("Ranking table")
    display = bowl_top[["rank", "player_name", "player_id", "pressure_bowling_rating", "pressure_economy", "normal_economy", "raw_normal_minus_pressure_economy", "pressure_wickets", "pressure_legal_balls", "matches_with_pressure_exposure", "consistency_rate", "consistency_evidence", "ipl_rating", "t20i_rating"]].copy()
    display.columns = ["Rank", "Bowler", "Player ID", "PBoR", "Pressure econ", "Normal econ", "Economy improvement", "Wickets", "Pressure legal balls", "Pressure matches", "Consistency", "Consistency evidence", "IPL rating", "T20I rating"]
    st.dataframe(display, hide_index=True, use_container_width=True, column_config={
        "PBoR": st.column_config.NumberColumn(format="%.2f"),
        "Pressure econ": st.column_config.NumberColumn(format="%.2f"),
        "Normal econ": st.column_config.NumberColumn(format="%.2f"),
        "Economy improvement": st.column_config.NumberColumn(format="%+.2f"),
        "Consistency": st.column_config.NumberColumn(format="%.0f%%"),
    })
    safe_download(bowl_top, "Download Top 10 bowlers CSV", "Top_10_Bowlers.csv", "dl_bowl_top")

    st.subheader("Inspect an individual bowler")
    chosen = st.selectbox("Select bowler", bowl_top["player_name"].tolist(), key="bowler_detail")
    row = bowl_top.loc[bowl_top.player_name == chosen].iloc[0]
    a, b, c, d = st.columns(4)
    with a: metric_card("Pressure economy", fmt_num(row.pressure_economy, 2), "Runs per over")
    with b: metric_card("Normal economy", fmt_num(row.normal_economy, 2), "Low-pressure baseline")
    with c: metric_card("Pressure wickets", fmt_int(row.pressure_wickets), "Credited wickets")
    with d: metric_card("Pressure legal balls", fmt_int(row.pressure_legal_balls), "Legal deliveries bowled")
    st.markdown(f"**Why this ranking?** {row.main_reason}")
    st.caption(f"90% match-bootstrap interval for pressure economy: {fmt_num(row.pressure_economy_90ci_low,2)}–{fmt_num(row.pressure_economy_90ci_high,2)}. Consistency evidence: {row.consistency_evidence}.")

elif page == "Player Explorer":
    st.markdown("<div class='section-kicker'>Full eligible player pool</div>", unsafe_allow_html=True)
    st.title("Player explorer")
    st.caption("Search and filter all eligible player-role records in the primary leaderboard.")
    role_filter = st.radio("Role", ["All", "Batter", "Bowler"], horizontal=True)
    search = st.text_input("Search by player name or ID", placeholder="e.g. Kohli or 6396")
    view = complete.copy()
    if role_filter != "All":
        view = view[view.role == role_filter]
    if search.strip():
        s = search.strip().lower()
        view = view[view.player_name.astype(str).str.lower().str.contains(s) | view.player_id.astype(str).str.contains(s)]
    view = view.sort_values(["role", "rank"])
    st.caption(f"Showing {len(view):,} eligible role-player entries.")
    st.dataframe(view, hide_index=True, use_container_width=True, column_config={
        "rating": st.column_config.NumberColumn(format="%.2f"),
        "pressure_metric": st.column_config.NumberColumn(format="%.2f"),
        "normal_metric": st.column_config.NumberColumn(format="%.2f"),
        "raw_delta": st.column_config.NumberColumn(format="%+.2f"),
        "matched_context_delta": st.column_config.NumberColumn(format="%+.2f"),
        "consistency": st.column_config.NumberColumn(format="%.0f%%"),
    })
    safe_download(view, "Download filtered leaderboard", "Filtered_Player_Leaderboard.csv", "dl_filtered_leaderboard")

    st.subheader("Player rating versus pressure exposure")
    role_chart = complete.copy()
    role_chart["pressure_exposure"] = pd.to_numeric(role_chart["pressure_exposure"], errors="coerce")
    role_chart["rating"] = pd.to_numeric(role_chart["rating"], errors="coerce")
    if role_filter != "All":
        role_chart = role_chart[role_chart.role == role_filter]
    fig = px.scatter(role_chart, x="pressure_exposure", y="rating", color="role", hover_name="player_name",
                     hover_data=["player_id", "hp_matches", "consistency"],
                     color_discrete_map={"Batter":"#55d6be", "Bowler":"#f1b65c"})
    fig.update_layout(xaxis_title="High-pressure exposure (balls)", yaxis_title="Composite rating")
    st.plotly_chart(chart_layout(fig, 380), use_container_width=True)

elif page == "IPL vs T20I":
    st.markdown("<div class='section-kicker'>Competition-specific view</div>", unsafe_allow_html=True)
    st.title("IPL vs T20I comparison")
    st.caption("The competition ratings are calculated separately. A player can have a result in one competition and no rating in the other.")
    role = st.radio("Choose role", ["Batters", "Bowlers"], horizontal=True)
    if role == "Batters":
        comp = bat_comp.copy()
        metric = "pressure_sr"
        base = "normal_sr"
        label = "Pressure strike rate"
        name_col = "striker_name"
        id_col = "striker_id"
    else:
        comp = bowl_comp.copy()
        metric = "pressure_economy"
        base = "normal_economy"
        label = "Pressure economy"
        name_col = "bowler_name"
        id_col = "bowler_id"
    if not comp.empty:
        q = st.text_input("Find a player", placeholder="Type a player name")
        if q.strip():
            comp = comp[comp[name_col].astype(str).str.contains(q.strip(), case=False, na=False)]
        min_exposure = st.slider("Minimum pressure exposure", 0, int(max(100, comp["pressure_balls" if role == "Batters" else "pressure_legal_balls"].max() if len(comp) else 100)), 0, 5)
        exposure_col = "pressure_balls" if role == "Batters" else "pressure_legal_balls"
        comp = comp[pd.to_numeric(comp[exposure_col], errors="coerce").fillna(0) >= min_exposure]
        st.dataframe(comp.sort_values("competition_rating", ascending=False), hide_index=True, use_container_width=True)
        player_names = sorted(comp[name_col].dropna().unique().tolist())
        if player_names:
            selected = st.selectbox("Compare a player across competitions", player_names)
            selected_df = comp[comp[name_col] == selected].sort_values("competition")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=selected_df["competition"], y=selected_df[metric], name=label,
                                 marker_color="#55d6be" if role == "Batters" else "#f1b65c"))
            fig.add_trace(go.Bar(x=selected_df["competition"], y=selected_df[base], name="Normal baseline",
                                 marker_color="#536987"))
            fig.update_layout(barmode="group", yaxis_title=label if role == "Batters" else "Runs per over", xaxis_title="Competition")
            st.plotly_chart(chart_layout(fig, 350), use_container_width=True)
            st.caption("A missing competition row means no qualifying/recorded comparison in that competition; it must not be interpreted as zero performance.")
        safe_download(comp, "Download competition comparison", f"{role.replace(' ', '_')}_IPL_T20I.csv", "dl_comp")

elif page == "Model & Data Audit":
    st.markdown("<div class='section-kicker'>Transparency and reproducibility</div>", unsafe_allow_html=True)
    st.title("Model, sensitivity & data audit")
    tabs = st.tabs(["Pressure Index", "Rating design", "Sensitivity", "Data quality", "Download report"])
    with tabs[0]:
        st.subheader("Pressure categories")
        st.markdown("| Pressure Index | Category |\n|---:|---|\n| 0–39 | Low |\n| 40–59 | Moderate |\n| 60–79 | High |\n| 80–100 | Extreme |")
        st.markdown("The model uses pre-delivery match state. It combines innings stage and wickets lost with first-innings scoring stress or second-innings chase difficulty. The precise construction and assumptions are documented in the methodology report.")
        if not phase_dist.empty:
            fig = px.bar(phase_dist, x="phase", y="deliveries", color="pressure_category", barmode="stack",
                         color_discrete_map={"Low":"#53718e", "Moderate":"#e3b45a", "High":"#ed875c", "Extreme":"#d95d78"})
            fig.update_layout(xaxis_title="Innings phase", yaxis_title="Deliveries")
            st.plotly_chart(chart_layout(fig, 340), use_container_width=True)
    with tabs[1]:
        st.subheader("Composite rating framework")
        weights = pd.DataFrame({"Component":["Performance quality under pressure", "Own-baseline improvement", "Match consistency", "Statistical reliability"],
                                "Weight":[50,25,15,10]})
        fig = px.bar(weights, x="Weight", y="Component", orientation="h", text="Weight", color="Component",
                     color_discrete_sequence=["#55d6be", "#5f87b5", "#e6b35d", "#d87987"])
        fig.update_layout(showlegend=False, xaxis_title="Weight (%)", yaxis_title="")
        st.plotly_chart(chart_layout(fig, 300), use_container_width=True)
        st.markdown("**Eligibility used in the primary run:** batters: ≥60 high-pressure balls and ≥5 pressure-exposure matches; bowlers: ≥36 high-pressure legal balls and ≥5 pressure-exposure matches. The pipeline also applies low-pressure baseline exposure requirements.")
        st.markdown("**Important:** PBR/PBoR are composite relative scores on a 0–100 display scale. They are not win probabilities, confidence probabilities, or measures of psychological composure.")
    with tabs[2]:
        st.subheader("Sensitivity to modelling choices")
        if not sensitivity.empty:
            st.dataframe(sensitivity[["pressure_threshold", "min_balls_batter", "min_legal_balls_bowler", "min_matches", "bat_overlap_primary", "bowl_overlap_primary"]], hide_index=True, use_container_width=True)
        if not weight_sensitivity.empty:
            st.markdown("**Top-10 overlap under alternative rating weights**")
            fig = px.bar(weight_sensitivity, x="weight_set", y="overlap_primary", color="role", barmode="group",
                         color_discrete_map={"Batter":"#55d6be", "Bowler":"#f1b65c"},
                         hover_data=["weights_quality_delta_consistency_reliability"])
            fig.update_layout(xaxis_title="Weight scenario", yaxis_title="Players retained from primary top 10", yaxis=dict(range=[0,10.5]))
            st.plotly_chart(chart_layout(fig, 350), use_container_width=True)
        st.markdown("**Interpretation:** The primary 60-threshold / 60-batter-ball / 36-bowler-ball / 5-match setting has full top-10 overlap under the primary weight set by definition. Alternative thresholds and weights change membership; consult the table rather than treating the ordering as assumption-free.")
    with tabs[3]:
        st.subheader("Source-data audit")
        keys = [
            ("Raw ball rows", "ball_rows_raw"), ("Analysed ball rows", "ball_rows_analysed"),
            ("Matches in analysis", "matches_in_analysis_scope_metadata"), ("No-result/abandoned excluded", "matches_excluded_no_result_or_abandoned"),
            ("Super-over rows excluded", "super_over_rows_excluded"), ("Exact duplicate rows", "exact_duplicate_rows_raw"),
            ("Wide deliveries", "wide_deliveries"), ("No-ball deliveries", "no_ball_deliveries_explicit_or_other"),
            ("Bowler-credited wickets", "bowler_credited_wickets"), ("Unknown 'other' extras", "unknown_other_extras"),
            ("Ambiguous player names", "ambiguous_player_names_different_ids"),
        ]
        cols = st.columns(3)
        for i, (label, key) in enumerate(keys):
            with cols[i % 3]:
                metric_card(label, fmt_int(audit.get(key)), "Source audit count")
        st.markdown("**Data-quality caveats from the audit**")
        st.markdown("- `extras_type=other` rows were treated as no-ball/non-legal based on their observed one-run pattern; a provider data dictionary is needed to confirm definitively.\n- Two non-zero extra rows were unlabelled and retained/flagged.\n- Innings totals/default chase targets were reconstructed from ball-by-ball records where revised targets were not supplied.\n- Seven player names map to multiple player IDs; IDs, rather than names alone, are the identity key.")
        with st.expander("View detailed audit JSON"):
            st.json(detailed_audit if detailed_audit else audit)
    with tabs[4]:
        st.subheader("Full methodology report")
        if REPORT_PATH.exists():
            st.download_button("Download PDF methodology report", REPORT_PATH.read_bytes(),
                               file_name=REPORT_PATH.name, mime="application/pdf", type="primary")
            st.caption("The report contains the full methodology, player rankings, charts, caveats and reproducibility notes.")
        else:
            st.warning("PDF report not found in assets/. Add the report file to enable downloads.")

st.sidebar.divider()
st.sidebar.caption("Data window: 22 Jan 2022 – 1 Nov 2026\nSource: supplied IPL + T20I ball-by-ball data pack.")
st.sidebar.caption("Built for the SupeRR Selector Season 2 Round 1 analysis.")

# Global download option
if page != "Model & Data Audit":
    with st.sidebar.expander("Download files"):
        safe_download(bat_top, "Top 10 batters CSV", "Top_10_Batters.csv", "side_bat")
        safe_download(bowl_top, "Top 10 bowlers CSV", "Top_10_Bowlers.csv", "side_bowl")
        safe_download(complete, "Complete leaderboard CSV", "Complete_Player_Leaderboard.csv", "side_all")

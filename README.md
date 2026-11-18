# SupeRR Selector Season 2 — Interactive Pressure Dashboard

An interactive Streamlit dashboard for exploring the precomputed IPL + T20I pressure-performance analysis (22 January 2022 to 1 November 2026).

## Dashboard sections

- **Overview:** coverage KPIs, pressure distribution and model leaders.
- **Top 10 Batters:** PBR rankings, pressure-vs-normal strike rate, sample size, consistency evidence and bootstrap interval.
- **Top 10 Bowlers:** PBoR rankings, pressure-vs-normal economy, wickets, exposure and uncertainty interval.
- **Player Explorer:** searchable eligible-player leaderboard and exposure-vs-rating plot.
- **IPL vs T20I:** competition-specific player comparison tables and charts.
- **Model & Data Audit:** pressure thresholds, score weights, sensitivity results, source-data audit and PDF report download.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## Deploy publicly with Streamlit Community Cloud

1. Create/sign in to GitHub.
2. Create a new GitHub repository, for example `superr-selector-pressure-dashboard`.
3. Upload the **contents** of this folder to the repository root (the `streamlit_app.py`, `requirements.txt`, `data/`, and `assets/` must be at the top level).
4. Open <https://share.streamlit.io/> and sign in with GitHub.
5. Select **Create app** → **Yup, I have an app**.
6. Choose your repository, branch (usually `main`), and main file path `streamlit_app.py`.
7. Deploy. Streamlit Community Cloud will build the app and assign a public `*.streamlit.app` URL.
8. Open that public URL in an incognito/private window to verify it is accessible without signing in. Paste the URL into the competition's dashboard-link field.

Official docs: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>

## Data and interpretation notes

This dashboard is a **presentation and exploration layer** over the CSV/JSON outputs created by the analysis pipeline. It does not rerun the original ball-by-ball model in the browser. To regenerate the underlying analysis, run `analyze_cricket.py` and then `finalize_deliverables.py` from the separate complete analysis package, then replace the dashboard's derived data files with the regenerated outputs.

- PBR and PBoR are composite relative scores on a 0–100 display scale, not probabilities.
- The Pressure Index is a match-state proxy, not a measurement of a player's mental state.
- High pressure is PI ≥ 60; extreme pressure is PI ≥ 80.
- The report documents eligibility, assumptions, data-quality caveats and sensitivity tests.
- The 111 MB delivery-level pressure export is intentionally not included; the dashboard uses compact player-level, match-level and aggregated result tables instead.

## Included files

- `streamlit_app.py` — interactive application.
- `requirements.txt` — pinned app dependencies.
- `data/` — derived leaderboard, comparison, pressure-distribution, sensitivity and audit files.
- `assets/` — full PDF methodology report.

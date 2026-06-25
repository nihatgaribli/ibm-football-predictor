"""
Soccer Tactical Analysis - Streamlit Application

An interactive web application for visualizing and analyzing soccer tracking data
using Voronoi diagrams and AI-powered tactical explanations.

Run with: streamlit run app.py
"""

import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st
import pandas as pd
import warnings

# Import configuration
from src.config import PAGE_CONFIG, OUTCOME_COLORS

# Import UI components
from src.ui_components import (
    get_theme_css,
    insight_card_html,
    make_dominance_gauge,
    extract_ai_insights
)

# Import visualization functions
from src.pitch_visualization import create_pitch_3d, create_soccer_pitch
from src.voronoi_visualization import (
    plot_voronoi_3d,
    plot_voronoi_2d,
    plot_shot_map,
    plot_dominance_timeline,
    compute_dominance_table
)

# Import data loaders
from src.data_loader import load_world_cup_matches, load_tracking_data

# Import analysis modules
from src.spatial_analysis import SoccerVoronoiAnalyzer
from src.tactical_explainer import TacticalExplainer
from statsbombpy import sb

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# ===========================================================================
# Page Configuration
# ===========================================================================

st.set_page_config(**PAGE_CONFIG)

# Initialize theme state
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = 'dark'

# Apply theme CSS
st.markdown(get_theme_css(st.session_state.theme_mode), unsafe_allow_html=True)

# ===========================================================================
# Main Application
# ===========================================================================

def main():
    """Main application function."""

    # Header
    st.markdown('<h1 class="main-header">Soccer Tactical Analysis</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Voronoi-based spatial control · AI tactical insights · World Cup 2022</p>',
        unsafe_allow_html=True
    )

    # Feature badges
    st.markdown(
        '<div class="badge-row">'
        '<span class="badge">🎯 Spatial Control</span>'
        '<span class="badge">🤖 AI Insights</span>'
        '<span class="badge">📊 Match Analytics</span>'
        '<span class="badge">🎥 3D Visualization</span>'
        '</div>',
        unsafe_allow_html=True
    )

    # ===========================================================================
    # Sidebar — Part 1: Theme + Match Selection
    # ===========================================================================
    with st.sidebar:
        # Load and display logo
        try:
            logo_path = src_path / "assets" / "logo.png"
            if logo_path.exists():
                with open(logo_path, "rb") as f:
                    logo_bytes = f.read()
                st.image(logo_bytes, use_container_width=True)
        except Exception as e:
            st.sidebar.error(f"Logo error: {e}")
            
        st.markdown("### Configuration")

        # Theme toggle — animated sun/moon switch
        is_light = st.session_state.theme_mode == 'light'
        # Inject CSS to style the toggle with sun/moon icons
        st.markdown("""
<style>
/* Theme toggle track */
div[data-testid="stToggle"] > label > div[role="switch"] {
    width: 56px !important;
    height: 28px !important;
    border-radius: 999px !important;
    transition: background 0.35s ease !important;
}
/* Dark mode: deep navy track */
div[data-testid="stToggle"] > label > div[role="switch"][aria-checked="false"] {
    background: linear-gradient(135deg, #1e3a5f, #0f172a) !important;
    border: 1px solid rgba(99,149,255,0.4) !important;
}
/* Light mode: warm sky track */
div[data-testid="stToggle"] > label > div[role="switch"][aria-checked="true"] {
    background: linear-gradient(135deg, #fbbf24, #f59e0b) !important;
    border: 1px solid rgba(251,191,36,0.5) !important;
}
/* Thumb (the circle that slides) */
div[data-testid="stToggle"] > label > div[role="switch"] > div {
    width: 22px !important;
    height: 22px !important;
    top: 3px !important;
    transition: transform 0.35s cubic-bezier(0.4,0,0.2,1) !important;
    font-size: 14px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: white !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.25) !important;
    border-radius: 50% !important;
}
/* Moon emoji on thumb when dark */
div[data-testid="stToggle"] > label > div[role="switch"][aria-checked="false"] > div::after {
    content: "🌙";
    font-size: 13px;
}
/* Sun emoji on thumb when light */
div[data-testid="stToggle"] > label > div[role="switch"][aria-checked="true"] > div::after {
    content: "☀️";
    font-size: 13px;
}
/* Toggle label text */
div[data-testid="stToggle"] > label > p {
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}
</style>
""", unsafe_allow_html=True)

        toggled = st.toggle(
            "Light Mode" if is_light else "Dark Mode",
            value=is_light,
            key="theme_toggle"
        )
        if toggled != is_light:
            st.session_state.theme_mode = 'light' if toggled else 'dark'
            st.rerun()

        st.markdown("---")

        # Match selection
        st.markdown("### Match Selection")
        matches = load_world_cup_matches()

        if not matches:
            st.error("No matches available")
            return

        # Filter out invalid entries (e.g., from old cached errors)
        valid_matches = {k: v for k, v in matches.items() if isinstance(v, dict)}

        if not valid_matches:
            st.error("No valid match data available. Try clearing the app cache.")
            return

        def _match_label(v):
            hs = v.get('home_score')
            aws = v.get('away_score')
            home = v.get('home', 'Unknown')
            away = v.get('away', 'Unknown')
            if hs is not None and aws is not None:
                return f"{home} {hs}–{aws} {away}"
            return f"{home} vs {away}"

        match_options = {_match_label(v): k for k, v in valid_matches.items()}
        selected_match_label = st.selectbox(
            "Select a match:",
            options=list(match_options.keys()),
            index=0
        )
        match_id = match_options[selected_match_label]
        match_info = valid_matches[match_id]

        hs = match_info.get('home_score')
        aws = match_info.get('away_score')
        score_str = f" **{hs}–{aws}**" if hs is not None else ""
        st.info(f"**{match_info.get('home', 'Unknown')}**{score_str} vs **{match_info.get('away', 'Unknown')}** · {match_info.get('date', '')}")

        st.markdown("---")

    # ===========================================================================
    # Load data (before sidebar shot selector so we can populate it)
    # ===========================================================================
    _progress_bar = st.progress(0, text="⏳ Loading match data…")
    _progress_bar.progress(10, text="📡 Connecting to StatsBomb…")

    tracking_df = load_tracking_data(match_id)
    _progress_bar.progress(60, text="🔍 Processing tracking data…")

    if tracking_df.empty:
        _progress_bar.empty()
        st.error("No tracking data available for this match")
        return

    # Load shot events
    try:
        _progress_bar.progress(80, text="⚽ Loading shot events…")
        events = sb.events(match_id=match_id)
        shot_events = events[events['type'] == 'Shot'].copy()
        _progress_bar.progress(100, text="✅ Data ready!")
    except Exception as e:
        _progress_bar.empty()
        st.error(f"Error loading shot events: {e}")
        shot_events = pd.DataFrame()

    _progress_bar.empty()

    # ===========================================================================
    # Sidebar — Part 2: Shot Selector + Analysis Options (requires loaded data)
    # ===========================================================================
    # Sort shot_ids by match minute (ascending) using shot_events metadata
    raw_shot_ids = set(tracking_df['shot_id'].unique())
    if not shot_events.empty and 'id' in shot_events.columns:
        # Keep only shots that have tracking data, sorted by minute then second
        ordered = (
            shot_events[shot_events['id'].isin(raw_shot_ids)]
            .sort_values(['minute', 'second'])['id']
            .tolist()
        )
        # Append any remaining IDs not found in shot_events (fallback)
        remaining = [sid for sid in sorted(raw_shot_ids) if sid not in ordered]
        shot_ids = ordered + remaining
    else:
        shot_ids = sorted(raw_shot_ids)

    if not shot_ids:
        st.warning("No shots with tracking data available")
        return

    # Build label map: shot_id -> "PlayerName (min') — Outcome"
    shot_label_map = {}
    for sid in shot_ids:
        if not shot_events.empty and 'id' in shot_events.columns:
            row = shot_events[shot_events['id'] == sid]
            if not row.empty:
                r = row.iloc[0]
                player = r.get('player', 'Unknown')
                minute = r.get('minute', '?')
                outcome = r.get('shot_outcome', '')
                shot_label_map[sid] = f"{player} ({minute}') — {outcome}"
            else:
                shot_label_map[sid] = f"Shot {str(sid)[:8]}..."
        else:
            shot_label_map[sid] = f"Shot {str(sid)[:8]}..."

    with st.sidebar:
        st.markdown("### Shot Selection")
        selected_shot_id = st.selectbox(
            "Select a shot to analyze:",
            options=shot_ids,
            format_func=lambda x: shot_label_map.get(x, f"Shot {str(x)[:8]}...")
        )

        st.markdown("---")
        st.markdown("### Analysis Options")

        view_mode = st.radio(
            "Visualization Mode:",
            ["3D Interactive", "2D Classic"],
            index=0
        )

        camera_preset = "🚁 Aerial"  # default fallback
        if view_mode == "3D Interactive":
            from src.config import CAMERA_PRESETS
            camera_preset = st.selectbox(
                "Camera Angle:",
                options=list(CAMERA_PRESETS.keys()),
                index=0
            )

        show_ai_insights = st.checkbox("Show AI Tactical Insights", value=True)
        show_match_overview = st.checkbox("Show Match Overview", value=True)

        st.markdown("---")
        st.markdown("### Shot Comparison")
        compare_mode = st.checkbox("Compare two shots side-by-side", value=False)
        if compare_mode:
            compare_shot_id = st.selectbox(
                "Compare with:",
                options=[sid for sid in shot_ids if sid != selected_shot_id],
                format_func=lambda x: shot_label_map.get(x, f"Shot {str(x)[:8]}...")
            )
        else:
            compare_shot_id = None

    # ===========================================================================
    # Resolve selected shot data early (needed for Match Overview highlight)
    # ===========================================================================
    shot_df = tracking_df[tracking_df['shot_id'] == selected_shot_id].copy()

    if shot_df.empty:
        st.warning("No data for selected shot")
        return

    # Get shot metadata
    shot_meta = None
    if not shot_events.empty and 'id' in shot_events.columns:
        shot_meta_rows = shot_events[shot_events['id'] == selected_shot_id]
        if not shot_meta_rows.empty:
            shot_meta = shot_meta_rows.iloc[0]

    # ===========================================================================
    # Match Overview — highlights the currently selected shot
    # ===========================================================================
    if show_match_overview and not shot_events.empty:
        st.markdown("## Match Overview")

        tab1, tab2, tab3 = st.tabs(["Shot Map", "Control Timeline", "Statistics"])

        with tab1:
            with st.container(border=True):
                # Pass selected shot ID so the map can highlight it
                fig_shots = plot_shot_map(shot_events, highlight_shot_id=selected_shot_id)
                st.plotly_chart(fig_shots, use_container_width=True)

        with tab2:
            with st.container(border=True):
                dom_table = compute_dominance_table(match_id, tracking_df, shot_events)
                if not dom_table.empty:
                    fig_timeline = plot_dominance_timeline(dom_table)
                    st.plotly_chart(fig_timeline, use_container_width=True)
                else:
                    st.info("No dominance data available")

        with tab3:
            st.markdown("##### Match Total")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Shots", len(shot_events))
            with col2:
                goals = len(shot_events[shot_events['shot_outcome'] == 'Goal'])
                st.metric("Goals", goals)
            with col3:
                if 'shot_statsbomb_xg' in shot_events.columns:
                    total_xg = shot_events['shot_statsbomb_xg'].sum()
                    st.metric("Total xG", f"{total_xg:.2f}")

    # ===========================================================================
    # Shot Analysis Section
    # ===========================================================================
    st.markdown("## Shot-by-Shot Analysis")

    # Shot info metrics
    if shot_meta is not None:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Player", shot_meta.get('player', 'Unknown'))
        with col2:
            st.metric("Minute", f"{shot_meta.get('minute', 0)}:{shot_meta.get('second', 0):02d}")
        with col3:
            st.metric("Outcome", shot_meta.get('shot_outcome', 'Unknown'))
        with col4:
            if 'shot_statsbomb_xg' in shot_meta:
                st.metric("xG", f"{shot_meta['shot_statsbomb_xg']:.2f}")

    # Analyze shot
    analyzer = SoccerVoronoiAnalyzer(pitch_length=120.0, pitch_width=80.0, attacking_third_start=80.0)

    try:
        analysis_result = analyzer.analyze_shot_event(shot_df)
    except Exception as e:
        st.error(f"Error analyzing shot: {e}")
        return

    # Visualization
    with st.container(border=True):
        att_teams = shot_df[shot_df['team_name'] != 'Opponent']['team_name'].unique()
        att_team = att_teams[0] if len(att_teams) > 0 else match_info['home']
        defending_team_name = match_info['away'] if att_team == match_info['home'] else match_info['home']

        shot_location = None
        highlight_player = None

        if show_ai_insights:
            most_space, most_tight, dom = extract_ai_insights(analysis_result)
            if most_space[0]:
                highlight_player = most_space[0]

            if shot_meta is not None and 'location' in shot_meta:
                loc = shot_meta['location']
                if isinstance(loc, (list, tuple)) and len(loc) >= 2:
                    shot_location = (loc[0], loc[1])

        if view_mode == "3D Interactive":
            fig = plot_voronoi_3d(
                shot_df,
                analyzer,
                defending_name=defending_team_name,
                camera_preset=camera_preset,
                shot_xy=shot_location,
                highlight_player=highlight_player
            )
        else:
            fig = plot_voronoi_2d(shot_df, analyzer, defending_name=defending_team_name)

        st.plotly_chart(fig, use_container_width=True)

        # Legend
        st.markdown(
            '<div class="legend-card">'
            '<strong>Legend:</strong><br>'
            '🔵 <strong>Attacking Team</strong> — team taking the shot<br>'
            '🔴 <strong>Defending Team</strong> — opposition<br>'
            '🟡 <strong>Goalkeeper</strong> — marked with gold ring<br>'
            '<em>Cell size = spatial control area (sq yards)</em>'
            '</div>',
            unsafe_allow_html=True
        )

    # AI Insights
    if show_ai_insights:
        st.markdown("## AI Tactical Insights")

        most_space, most_tight, dom = extract_ai_insights(analysis_result)

        col1, col2, col3 = st.columns(3)

        with col1:
            if most_space[0]:
                st.markdown(
                    insight_card_html(
                        "🎯", "Most Space",
                        most_space[0], f"{most_space[1]:.0f} sq yd", "#10b981"
                    ),
                    unsafe_allow_html=True
                )

        with col2:
            if most_tight[0]:
                st.markdown(
                    insight_card_html(
                        "🔒", "Most Pressured",
                        most_tight[0], f"{most_tight[1]:.0f} sq yd", "#ef4444"
                    ),
                    unsafe_allow_html=True
                )

        with col3:
            att_dom = dom.get('Attacking Team', 0)
            st.markdown(
                insight_card_html(
                    "⚡", "Attacking Control",
                    f"{att_dom:.1f}%", "in attacking third", "#38bdf8"
                ),
                unsafe_allow_html=True
            )

        # Dominance gauge
        with st.container(border=True):
            attacking_team = (
                shot_df[shot_df['team_name'] != 'Opponent']['team_name'].iloc[0]
                if 'Opponent' in shot_df['team_name'].values
                else shot_df['team_name'].iloc[0]
            )
            fig_gauge = make_dominance_gauge(att_dom, attacking_team)
            st.plotly_chart(fig_gauge, use_container_width=True)

        # AI Explanation
        with st.container(border=True):
            st.markdown("### Tactical Explanation")

            try:
                explainer = TacticalExplainer()
                explanation = explainer.generate_explanation(analysis_result)
                st.markdown(
                    f'<div class="explanation-box">{explanation}</div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.info(f"AI explanation temporarily unavailable: {e}")

    # Footer
    st.markdown("---")
    st.markdown(
        '<div class="footer-text">'
        '⚽ <strong>Soccer Tactical Analysis</strong> · '
        'Powered by StatsBomb Open Data · '
        'Built with Streamlit & Plotly'
        '</div>',
        unsafe_allow_html=True
    )

    # ===========================================================================
    # Shot Comparison Section
    # ===========================================================================
    if compare_mode and compare_shot_id is not None:
        st.markdown("---")
        st.markdown("## Shot Comparison")

        # Gather data for both shots
        shot_df_b   = tracking_df[tracking_df['shot_id'] == compare_shot_id].copy()
        shot_meta_b = None
        if not shot_events.empty and 'id' in shot_events.columns:
            rows_b = shot_events[shot_events['id'] == compare_shot_id]
            if not rows_b.empty:
                shot_meta_b = rows_b.iloc[0]

        def _get_meta_str(meta, field, default='—'):
            if meta is None:
                return default
            v = meta.get(field, default)
            return str(v) if v is not None else default

        def _render_shot_col(df, meta, label, col_key: str):
            """Render one shot column: metrics + Voronoi map."""
            st.markdown(f"##### {label}")
            # Metrics: 2x2 grid (wider boxes → full names fit)
            m1, m2 = st.columns(2)
            m1.metric("Player",  _get_meta_str(meta, 'player'))
            m2.metric("Minute",  f"{_get_meta_str(meta,'minute','?')}:{_get_meta_str(meta,'second','00').zfill(2)}")
            m3, m4 = st.columns(2)
            m3.metric("Outcome", _get_meta_str(meta, 'shot_outcome'))
            xg_val = meta.get('shot_statsbomb_xg') if meta is not None else None
            m4.metric("xG", f"{xg_val:.2f}" if xg_val is not None else '—')

            att_teams = df[df['team_name'] != 'Opponent']['team_name'].unique()
            att_team = att_teams[0] if len(att_teams) > 0 else match_info['home']
            def_name = match_info['away'] if att_team == match_info['home'] else match_info['home']
            try:
                res = analyzer.analyze_shot_event(df)
            except Exception:
                res = None

            hl_player = None
            shot_loc   = None
            if res and show_ai_insights:
                sp, _, _ = extract_ai_insights(res)
                hl_player = sp[0] if sp[0] else None
            if meta is not None and 'location' in meta:
                loc = meta['location']
                if isinstance(loc, (list, tuple)) and len(loc) >= 2:
                    shot_loc = (loc[0], loc[1])

            with st.container(border=True):
                if view_mode == "3D Interactive":
                    fig_c = plot_voronoi_3d(
                        df, analyzer,
                        defending_name=def_name,
                        camera_preset=camera_preset,
                        shot_xy=shot_loc,
                        highlight_player=hl_player
                    )
                else:
                    fig_c = plot_voronoi_2d(df, analyzer, defending_name=def_name)
                st.plotly_chart(fig_c, use_container_width=True, key=f"cmp_chart_{col_key}")

            # Quick AI insight summary
            if res and show_ai_insights:
                sp, st_tight, dom_c = extract_ai_insights(res)
                att_dom_c = dom_c.get('Attacking Team', 0)
                ic1, ic2, ic3 = st.columns(3)
                if sp[0]:
                    ic1.markdown(insight_card_html("🎯","Most Space", sp[0], f"{sp[1]:.0f} sq yd","#10b981"), unsafe_allow_html=True)
                if st_tight[0]:
                    ic2.markdown(insight_card_html("🔒","Most Pressured", st_tight[0], f"{st_tight[1]:.0f} sq yd","#ef4444"), unsafe_allow_html=True)
                ic3.markdown(insight_card_html("⚡","Att. Control", f"{att_dom_c:.1f}%","in attacking third","#38bdf8"), unsafe_allow_html=True)

        col_a, col_b = st.columns(2, gap="medium")
        with col_a:
            label_a = shot_label_map.get(selected_shot_id, "Shot A")
            _render_shot_col(shot_df, shot_meta, f"🅐 {label_a}", col_key="a")
        with col_b:
            label_b = shot_label_map.get(compare_shot_id, "Shot B")
            _render_shot_col(shot_df_b, shot_meta_b, f"🅑 {label_b}", col_key="b")


if __name__ == "__main__":
    main()

# Made with Bob

"""
Voronoi Visualization Module

This module contains functions for creating Voronoi diagrams and spatial analysis
visualizations in both 2D and 3D, including shot maps and dominance timelines.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.spatial import Voronoi
from typing import Optional, Tuple, Dict, Any

from .config import (
    PITCH_LENGTH, PITCH_WIDTH, ATTACKING_THIRD_X,
    ATTACK_HEX, ATTACK_FILL, DEFEND_HEX, DEFEND_FILL,
    GK_HEX, OUTCOME_COLORS
)
from .pitch_visualization import create_pitch_3d, create_soccer_pitch, cell_exterior
from .spatial_analysis import SoccerVoronoiAnalyzer


# ===========================================================================
# Team Assignment Helper
# ===========================================================================

def assign_teams(shot_df: pd.DataFrame, defending_name: Optional[str] = None) -> Tuple:
    """
    Determine which unique team is attacking vs defending and build colour maps.
    
    Parameters
    ----------
    shot_df : pd.DataFrame
        DataFrame containing shot data with team_name column
    defending_name : str, optional
        Real name of the defending team (the opponent of the shooting team).
        Used to label the 'Opponent' placeholder with the actual team name.
        
    Returns
    -------
    tuple
        (attacking_team, defending_team, name_map, fill_map, marker_map)
    """
    unique_teams = list(shot_df['team_name'].unique())

    opp_label = defending_name if defending_name else 'Defending Team'
    name_map = {}
    for team in unique_teams:
        name_map[team] = opp_label if team == 'Opponent' else team

    # The shooting team's players carry the real team name (e.g. "France"); the
    # opposition is tagged "Opponent". The team taking the shot is ALWAYS the
    # attacker, so colours stay consistent across every shot and every match.
    defending_team = 'Opponent' if 'Opponent' in unique_teams else None
    attacking_team = next((t for t in unique_teams if t not in ('Opponent', 'Unknown')), None)

    # Fallbacks for unusual data
    if attacking_team is None and unique_teams:
        attacking_team = unique_teams[0]
    if defending_team is None:
        defending_team = next((t for t in unique_teams if t != attacking_team), attacking_team)

    fill_map, marker_map = {}, {}
    for team in unique_teams:
        if team == attacking_team:
            fill_map[team] = ATTACK_FILL
            marker_map[team] = {'color': ATTACK_HEX, 'symbol_2d': 'triangle-up', 'symbol_3d': 'diamond'}
        else:
            fill_map[team] = DEFEND_FILL
            marker_map[team] = {'color': DEFEND_HEX, 'symbol_2d': 'square', 'symbol_3d': 'square'}

    return attacking_team, defending_team, name_map, fill_map, marker_map


# ===========================================================================
# 3D Voronoi Visualization
# ===========================================================================

def plot_voronoi_3d(
    shot_df: pd.DataFrame,
    analyzer: SoccerVoronoiAnalyzer,
    defending_name: Optional[str] = None,
    camera_preset: str = "🚁 Aerial",
    shot_xy: Optional[Tuple[float, float]] = None,
    highlight_player: Optional[str] = None
) -> go.Figure:
    """
    Render the Voronoi spatial-control map as clean, flat coloured tiles on a
    tilted 3D pitch. Players sit on short vertical pins above their territory.
    
    Parameters
    ----------
    shot_df : pd.DataFrame
        DataFrame containing player positions and team information
    analyzer : SoccerVoronoiAnalyzer
        Analyzer instance for computing Voronoi cells
    defending_name : str, optional
        Name of the defending team
    camera_preset : str, optional
        Camera view preset (default: "🚁 Aerial")
    shot_xy : tuple, optional
        (x, y) origin of the shot — draws a marker + arrow to goal
    highlight_player : str, optional
        Name of the player to spotlight (the "exploitable gap")
        
    Returns
    -------
    go.Figure
        Plotly 3D figure with Voronoi diagram
    """
    fig = create_pitch_3d(camera_preset)

    points = shot_df[['x', 'y']].values
    if len(points) < 3:
        st.warning("Not enough players for Voronoi diagram (minimum 3 required)")
        return fig

    extended_points = analyzer._add_boundary_points(points)
    try:
        vor = Voronoi(extended_points)
    except Exception as e:
        st.error(f"Error computing Voronoi: {e}")
        return fig

    attacking_team, defending_team, name_map, fill_map, marker_map = assign_teams(
        shot_df, defending_name)

    Z_CELL = 0.55      # flat tile height above grass
    Z_PIN_TOP = 3.6    # player marker height

    # Compute each player's bounded Voronoi cell once
    players = []
    for pos, (idx, row) in enumerate(shot_df.iterrows()):
        cell = analyzer._compute_voronoi_cell(vor, pos)
        area = cell.area if (cell is not None and not cell.is_empty) else 0.0
        players.append({
            'x': float(row['x']), 'y': float(row['y']),
            'team': row['team_name'], 'name': row['player_name'],
            'is_gk': bool(row.get('is_goalkeeper', False)),
            'cell': cell, 'area': area
        })

    # --- Flat coloured tiles (Mesh3d top face) + batched white borders ---
    border_x, border_y, border_z = [], [], []
    for p in players:
        cell = p['cell']
        if cell is None or cell.is_empty:
            continue
        try:
            xs, ys = cell_exterior(cell)
        except Exception:
            continue
        n = len(xs)
        if n < 3:
            continue
        # Fan triangulation of the (convex) cell as a flat polygon
        I = [0] * (n - 2)
        J = list(range(1, n - 1))
        K = list(range(2, n))
        fill_hex = ATTACK_HEX if p['team'] == attacking_team else DEFEND_HEX
        fig.add_trace(go.Mesh3d(
            x=xs, y=ys, z=[Z_CELL] * n, i=I, j=J, k=K,
            color=fill_hex, opacity=0.95, flatshading=True,
            lighting=dict(ambient=0.9, diffuse=0.4, specular=0.05),
            hovertext=f"{p['name']} — {p['area']:.0f} sq yd",
            hoverinfo='text', showlegend=False
        ))
        border_x += xs + [xs[0], None]
        border_y += ys + [ys[0], None]
        border_z += [Z_CELL + 0.05] * (n + 1) + [None]

    if border_x:
        fig.add_trace(go.Scatter3d(
            x=border_x, y=border_y, z=border_z, mode='lines',
            line=dict(color='rgba(255,255,255,0.95)', width=3.5),
            hoverinfo='skip', showlegend=False
        ))

    # --- Players: short vertical pins + markers on top ---
    for team in shot_df['team_name'].unique():
        team_players = [p for p in players if p['team'] == team]
        if not team_players:
            continue
        mp = marker_map.get(team, {'color': '#888', 'symbol_3d': 'circle'})

        sx, sy, sz = [], [], []
        for p in team_players:
            sx += [p['x'], p['x'], None]
            sy += [p['y'], p['y'], None]
            sz += [Z_CELL, Z_PIN_TOP, None]
        fig.add_trace(go.Scatter3d(
            x=sx, y=sy, z=sz, mode='lines',
            line=dict(color=mp['color'], width=3),
            opacity=0.65, hoverinfo='skip', showlegend=False
        ))

        fig.add_trace(go.Scatter3d(
            x=[p['x'] for p in team_players],
            y=[p['y'] for p in team_players],
            z=[Z_PIN_TOP] * len(team_players),
            mode='markers',
            marker=dict(size=8, color=mp['color'], symbol=mp['symbol_3d'],
                        line=dict(color='white', width=1.5), opacity=0.98),
            name=name_map.get(team, team),
            text=[p['name'] for p in team_players],
            customdata=[[p['area']] for p in team_players],
            hovertemplate='<b>%{text}</b><br>Pos: (%{x:.0f}, %{y:.0f})'
                          '<br>Control: %{customdata[0]:.0f} sq yd<extra></extra>'
        ))

    # Goalkeeper ring overlay
    gk = [p for p in players if p['is_gk']]
    if gk:
        fig.add_trace(go.Scatter3d(
            x=[p['x'] for p in gk], y=[p['y'] for p in gk],
            z=[Z_PIN_TOP] * len(gk),
            mode='markers',
            marker=dict(size=14, color='rgba(0,0,0,0)', symbol='circle-open',
                        line=dict(color=GK_HEX, width=3)),
            showlegend=False, hoverinfo='skip'
        ))

    # --- AI insight overlays ---
    import streamlit as st
    is_light = st.session_state.get('theme_mode', 'dark') == 'light'
    text_col = '#1e293b' if is_light else 'white'

    if shot_xy is not None:
        sx0, sy0 = float(shot_xy[0]), float(shot_xy[1])
        gx, gy = PITCH_LENGTH, PITCH_WIDTH / 2
        fig.add_trace(go.Scatter3d(
            x=[sx0, gx], y=[sy0, gy], z=[Z_PIN_TOP, Z_PIN_TOP], mode='lines',
            line=dict(color='rgba(255,255,255,0.9)', width=5, dash='dash'),
            hoverinfo='skip', showlegend=False))
        fig.add_trace(go.Cone(
            x=[gx], y=[gy], z=[Z_PIN_TOP],
            u=[gx - sx0], v=[gy - sy0], w=[0],
            sizemode='absolute', sizeref=4, anchor='tip',
            colorscale=[[0, '#ffffff'], [1, '#ffffff']], showscale=False,
            hoverinfo='skip'))
        
        fig.add_trace(go.Scatter3d(
            x=[sx0], y=[sy0], z=[Z_PIN_TOP], mode='markers+text',
            marker=dict(size=9, color='#ffffff', symbol='diamond',
                        line=dict(color='#0ea5e9', width=2)),
            text=["⚽ shot"], textposition="top center",
            textfont=dict(color=text_col, size=11),
            hoverinfo='skip', showlegend=False))

    if highlight_player:
        hp = next((p for p in players if p['name'] == highlight_player), None)
        if hp is not None:
            fig.add_trace(go.Scatter3d(
                x=[hp['x']], y=[hp['y']], z=[Z_PIN_TOP], mode='markers+text',
                marker=dict(size=20, color='rgba(251,191,36,0.0)', symbol='circle-open',
                            line=dict(color=GK_HEX, width=4)),
                text=[f"⭐ {hp['name'].split()[-1]}"], textposition="bottom center",
                textfont=dict(color=GK_HEX, size=12),
                hoverinfo='skip', showlegend=False))

    short_id = str(shot_df['shot_id'].iloc[0])[:8]
    fig.update_layout(
        title=dict(text=f"⚽ Spatial Control Map — Shot {short_id}…",
                   x=0.5, xanchor='center', font=dict(color=text_col, size=18))
    )
    return fig


# ===========================================================================
# 2D Voronoi Visualization
# ===========================================================================

def plot_voronoi_2d(
    shot_df: pd.DataFrame,
    analyzer: SoccerVoronoiAnalyzer,
    defending_name: Optional[str] = None
) -> go.Figure:
    """Plot Voronoi diagram on a 2D soccer pitch using Plotly."""
    fig = create_soccer_pitch()

    points = shot_df[['x', 'y']].values
    if len(points) < 3:
        st.warning("Not enough players for Voronoi diagram (minimum 3 required)")
        return fig

    extended_points = analyzer._add_boundary_points(points)
    try:
        vor = Voronoi(extended_points)
    except Exception as e:
        st.error(f"Error computing Voronoi: {e}")
        return fig

    attacking_team, defending_team, name_map, fill_map, marker_map = assign_teams(
        shot_df, defending_name)

    # Voronoi cells
    for pos, (idx, row) in enumerate(shot_df.iterrows()):
        cell = analyzer._compute_voronoi_cell(vor, pos)
        if cell is not None and not cell.is_empty:
            x_coords, y_coords = cell.exterior.xy
            if row['team_name'] == attacking_team:
                color = 'rgba(46, 155, 255, 0.95)'
            elif row['team_name'] == defending_team:
                color = 'rgba(255, 77, 94, 0.95)'
            else:
                color = 'rgba(128, 128, 128, 0.95)'
            
            fig.add_trace(go.Scatter(
                x=list(x_coords), y=list(y_coords),
                fill='toself', fillcolor=color,
                line=dict(color='rgba(255, 255, 255, 0.95)', width=3),
                mode='lines',
                name=f"{row['player_name']} ({name_map.get(row['team_name'], row['team_name'])})",
                hoverinfo='name', showlegend=False
            ))

    # Player markers
    for team_name in shot_df['team_name'].unique():
        team_df = shot_df[shot_df['team_name'] == team_name].copy()
        mp = marker_map.get(team_name, {'color': 'gray', 'symbol_2d': 'circle'})
        
        fig.add_trace(go.Scatter(
            x=team_df['x'], y=team_df['y'],
            mode='markers',
            marker=dict(
                size=40,
                color=mp['color'],
                line=dict(color='white', width=4),
                symbol=mp['symbol_2d'],
                opacity=1.0
            ),
            name=name_map.get(team_name, team_name),
            text=team_df['player_name'],
            hovertemplate='<b>%{text}</b><br>Position: (%{x:.1f}, %{y:.1f})<extra></extra>',
            hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.95)", font_size=14,
                            font_family="Poppins", font_color="black")
        ))

    short_id = str(shot_df['shot_id'].iloc[0])[:8]
    import streamlit as st
    is_light = st.session_state.get('theme_mode', 'dark') == 'light'
    text_col = '#1e293b' if is_light else 'white'
    
    fig.update_layout(title=dict(text=f"Voronoi Spatial Analysis — Shot {short_id}…",
                                 x=0.5, font=dict(size=18, color=text_col)))
    return fig


# ===========================================================================
# Analysis Functions
# ===========================================================================

@st.cache_data(show_spinner=False)
def compute_dominance_table(match_id: int, _tracking_df: pd.DataFrame, _shot_events: pd.DataFrame) -> pd.DataFrame:
    """Run Voronoi analysis across every tracked shot and merge with shot metadata."""
    analyzer = SoccerVoronoiAnalyzer(pitch_length=120.0, pitch_width=80.0, attacking_third_start=80.0)
    rows = []
    for sid, g in _tracking_df.groupby('shot_id'):
        try:
            r = analyzer.analyze_shot_event(g)
            rows.append(dict(
                shot_id=sid,
                attacking_dom=r['team_dominance']['Attacking Team'],
                defending_dom=r['team_dominance']['Defending Team'],
                coverage=r['total_pitch_coverage'],
            ))
        except Exception:
            continue
    dom = pd.DataFrame(rows)
    if dom.empty:
        return dom
    keep = [c for c in ['id', 'minute', 'second', 'player', 'team',
                        'shot_outcome', 'shot_statsbomb_xg'] if c in _shot_events.columns]
    meta = _shot_events[keep].copy()
    out = dom.merge(meta, left_on='shot_id', right_on='id', how='left')
    out = out.sort_values(['minute', 'second']).reset_index(drop=True)
    return out


def plot_shot_map(shot_events: pd.DataFrame, highlight_shot_id=None) -> go.Figure:
    """Plot all shots of the match on a 2D pitch, sized by xG and coloured by outcome.
    
    Parameters
    ----------
    shot_events : pd.DataFrame
        All shot events for the match.
    highlight_shot_id : optional
        The shot ID to highlight (draws a large glowing ring around it).
    """
    fig = create_soccer_pitch()
    import streamlit as st
    is_light = st.session_state.get('theme_mode', 'dark') == 'light'
    text_color = '#1e293b' if is_light else 'white'
    
    fig.update_layout(
        height=560, 
        title=dict(text="Shot Map — sized by xG, coloured by outcome", x=0.5, xanchor='center', font=dict(color=text_color)),
        hoverlabel=dict(bgcolor="white" if is_light else "#0f172a", font_size=14,
                        font_family="Poppins", font_color="#1e293b" if is_light else "white")
    )
    if 'location' not in shot_events.columns:
        return fig

    df = shot_events.copy()
    df = df[df['location'].notna()]
    df['sx'] = df['location'].apply(lambda v: v[0] if isinstance(v, (list, tuple)) and len(v) > 0 else None)
    df['sy'] = df['location'].apply(lambda v: v[1] if isinstance(v, (list, tuple)) and len(v) > 1 else None)
    df = df.dropna(subset=['sx', 'sy'])
    if 'shot_statsbomb_xg' not in df.columns:
        df['shot_statsbomb_xg'] = 0.05
    df['shot_statsbomb_xg'] = df['shot_statsbomb_xg'].fillna(0.03)
    if 'shot_outcome' not in df.columns:
        df['shot_outcome'] = 'Unknown'

    for outcome, g in df.groupby('shot_outcome'):
        color = OUTCOME_COLORS.get(outcome, '#94a3b8')
        is_goal = outcome == 'Goal'
        fig.add_trace(go.Scatter(
            x=g['sx'], y=g['sy'], mode='markers',
            marker=dict(
                size=(8 + g['shot_statsbomb_xg'] * 46),
                color=color, symbol='star' if is_goal else 'circle',
                line=dict(color='white', width=2 if is_goal else 1),
                opacity=0.95,
            ),
            name=f"⭐ {outcome}" if is_goal else outcome,
            text=g['player'] if 'player' in g.columns else None,
            customdata=np.stack([
                g['shot_statsbomb_xg'],
                g['minute'] if 'minute' in g.columns else np.zeros(len(g)),
            ], axis=-1),
            hovertemplate='<b>%{text}</b><br>xG: %{customdata[0]:.2f}'
                          '<br>Minute: %{customdata[1]:.0f}'
                          f'<br>Outcome: {outcome}<extra></extra>',
        ))

    # Highlight the selected shot with a glowing ring
    if highlight_shot_id is not None and 'id' in df.columns:
        sel = df[df['id'] == highlight_shot_id]
        if not sel.empty:
            r = sel.iloc[0]
            player_name = r.get('player', 'Selected Shot')
            fig.add_trace(go.Scatter(
                x=[r['sx']], y=[r['sy']],
                mode='markers',
                marker=dict(
                    size=38,
                    color='rgba(0,0,0,0)',
                    line=dict(color='#FBBF24', width=4),
                    symbol='circle',
                ),
                name=f"▶ {player_name}",
                hovertemplate=f'<b>Selected: {player_name}</b><extra></extra>',
                showlegend=True,
            ))

    return fig



def plot_dominance_timeline(dom_df: pd.DataFrame) -> go.Figure:
    """Plot attacking-team control share across the match timeline."""
    fig = go.Figure()
    if dom_df is None or dom_df.empty:
        return fig

    d = dom_df.dropna(subset=['minute']).copy()
    fig.add_hrect(y0=0, y1=50, fillcolor="rgba(255,77,94,0.06)", line_width=0)
    fig.add_hrect(y0=50, y1=100, fillcolor="rgba(46,155,255,0.06)", line_width=0)
    import streamlit as st
    is_light = st.session_state.get('theme_mode', 'dark') == 'light'
    
    text_col = '#1e293b' if is_light else 'white'
    grid_col = 'rgba(0, 0, 0, 0.08)' if is_light else 'rgba(255, 255, 255, 0.08)'
    axis_col = 'rgba(0, 0, 0, 0.6)' if is_light else 'rgba(255, 255, 255, 0.7)'
    dash_col = 'rgba(0, 0, 0, 0.2)' if is_light else 'rgba(255, 255, 255, 0.35)'
    legend_bg = 'rgba(255, 255, 255, 0.8)' if is_light else 'rgba(15, 23, 42, 0.6)'
    legend_border = 'rgba(0, 0, 0, 0.1)' if is_light else 'rgba(255, 255, 255, 0.2)'

    fig.add_hline(y=50, line=dict(color=dash_col, width=1, dash="dash"))

    fig.add_trace(go.Scatter(
        x=d['minute'], y=d['attacking_dom'], mode='lines+markers',
        line=dict(color="#38bdf8", width=3, shape='spline'),
        marker=dict(size=9, color="#38bdf8", line=dict(color=text_col, width=1)),
        name="Attacking control %",
        text=d['player'] if 'player' in d.columns else None,
        hovertemplate="<b>%{text}</b><br>Min %{x:.0f}<br>Control: %{y:.1f}%<extra></extra>",
    ))

    if 'shot_outcome' in d.columns:
        goals = d[d['shot_outcome'] == 'Goal']
        if not goals.empty:
            fig.add_trace(go.Scatter(
                x=goals['minute'], y=goals['attacking_dom'], mode='markers',
                marker=dict(size=18, color="#FBBF24", symbol='star',
                            line=dict(color=text_col, width=1.5)),
                name="⚽ Goal",
                text=goals['player'] if 'player' in goals.columns else None,
                hovertemplate="<b>GOAL — %{text}</b><br>Min %{x:.0f}<extra></extra>",
            ))

    fig.update_layout(
        height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Poppins", color=text_col),
        margin=dict(l=40, r=20, t=50, b=40),
        title=dict(text="Attacking-Third Control Through the Match", x=0.5, xanchor='center',
                   font=dict(color=text_col, family="Poppins")),
        xaxis=dict(
            title=dict(text="Match minute", font=dict(color=text_col)),
            gridcolor=grid_col, zeroline=False, color=axis_col,
            tickfont=dict(color=text_col, family="Poppins"),
        ),
        yaxis=dict(
            title=dict(text="Attacking control %", font=dict(color=text_col)),
            range=[0, 100], gridcolor=grid_col, zeroline=False, color=axis_col,
            tickfont=dict(color=text_col, family="Poppins"),
        ),
        legend=dict(bgcolor=legend_bg, bordercolor=legend_border,
                    borderwidth=1, font=dict(color=text_col)),
        hoverlabel=dict(bgcolor="white" if is_light else "#0f172a", font_size=14,
                        font_family="Poppins", font_color="#1e293b" if is_light else "white")
    )
    return fig

# Made with Bob

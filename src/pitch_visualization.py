"""
Pitch Visualization Module

This module contains functions for creating 2D and 3D soccer pitch visualizations
using Plotly, including geometry helpers and pitch markings.
"""

import numpy as np
import plotly.graph_objects as go
from typing import Tuple, List, Union
from .config import (
    PITCH_LENGTH, PITCH_WIDTH, ATTACKING_THIRD_X,
    LINE_COLOR, THIRD_GOLD, CAMERA_PRESETS
)


# ===========================================================================
# Geometry Helper Functions
# ===========================================================================

def circle_xy(cx: float, cy: float, r: float, n: int = 80) -> Tuple[np.ndarray, np.ndarray]:
    """
    Return x, y coordinate arrays tracing a full circle.
    
    Parameters
    ----------
    cx : float
        Center x coordinate
    cy : float
        Center y coordinate
    r : float
        Radius
    n : int, optional
        Number of points (default: 80)
        
    Returns
    -------
    tuple
        (x_coords, y_coords) arrays
    """
    t = np.linspace(0, 2 * np.pi, n)
    return cx + r * np.cos(t), cy + r * np.sin(t)


def arc_xy(cx: float, cy: float, r: float, a0: float, a1: float, n: int = 40) -> Tuple[np.ndarray, np.ndarray]:
    """
    Return x, y coordinate arrays tracing an arc between two angles (radians).
    
    Parameters
    ----------
    cx : float
        Center x coordinate
    cy : float
        Center y coordinate
    r : float
        Radius
    a0 : float
        Start angle in radians
    a1 : float
        End angle in radians
    n : int, optional
        Number of points (default: 40)
        
    Returns
    -------
    tuple
        (x_coords, y_coords) arrays
    """
    t = np.linspace(a0, a1, n)
    return cx + r * np.cos(t), cy + r * np.sin(t)


def cell_exterior(cell) -> Tuple[List[float], List[float]]:
    """
    Extract exterior (x, y) vertex lists from a shapely polygon, sans closing duplicate.
    
    Parameters
    ----------
    cell : shapely.geometry.Polygon
        Polygon to extract vertices from
        
    Returns
    -------
    tuple
        (x_coords, y_coords) lists
    """
    coords = list(cell.exterior.coords)
    if len(coords) > 1 and coords[0] == coords[-1]:
        coords = coords[:-1]
    xs = [float(p[0]) for p in coords]
    ys = [float(p[1]) for p in coords]
    return xs, ys


# ===========================================================================
# 3D Pitch Visualization
# ===========================================================================

def create_pitch_3d(camera_preset: str = "🚁 Aerial") -> go.Figure:
    """
    Create a Plotly 3D figure with a textured grass plane and pitch markings.
    
    Parameters
    ----------
    camera_preset : str, optional
        Camera view preset (default: "🚁 Aerial")
        Options: "🚁 Aerial", "📺 Broadcast", "🥅 Behind Goal", "🗺️ Top-Down"
        
    Returns
    -------
    go.Figure
        Plotly 3D figure with pitch
    """
    fig = go.Figure()

    # --- Grass plane with mowed-lawn stripes ---
    gx = np.linspace(0, PITCH_LENGTH, 121)
    gy = np.linspace(0, PITCH_WIDTH, 81)
    GX, _ = np.meshgrid(gx, gy)
    GZ = np.zeros((len(gy), len(gx)))
    stripe = (np.floor(GX / 8.0).astype(int) % 2).astype(float)

    fig.add_trace(go.Surface(
        x=gx, y=gy, z=GZ,
        surfacecolor=stripe,
        colorscale=[[0, '#11823f'], [1, '#0c6a31']],
        showscale=False,
        opacity=1.0,
        lighting=dict(ambient=0.78, diffuse=0.55, specular=0.04, roughness=0.95),
        hoverinfo='skip',
        showlegend=False,
        name='Pitch'
    ))

    z_line = 0.35  # markings float just above the grass

    def add_line(xs: Union[List[float], np.ndarray], ys: Union[List[float], np.ndarray],
                 color: str = LINE_COLOR, width: int = 4):
        """Add a line to the 3D pitch."""
        fig.add_trace(go.Scatter3d(
            x=list(xs), y=list(ys), z=[z_line] * len(xs),
            mode='lines',
            line=dict(color=color, width=width),
            hoverinfo='skip', showlegend=False
        ))

    def add_spot(cx: float, cy: float):
        """Add a spot marker to the 3D pitch."""
        fig.add_trace(go.Scatter3d(
            x=[cx], y=[cy], z=[z_line],
            mode='markers',
            marker=dict(size=3, color='white'),
            hoverinfo='skip', showlegend=False
        ))

    # Outer boundary
    add_line([0, PITCH_LENGTH, PITCH_LENGTH, 0, 0], [0, 0, PITCH_WIDTH, PITCH_WIDTH, 0])
    
    # Halfway line
    add_line([PITCH_LENGTH / 2, PITCH_LENGTH / 2], [0, PITCH_WIDTH])
    
    # Center circle + spot
    cx, cy = circle_xy(PITCH_LENGTH / 2, PITCH_WIDTH / 2, 10)
    add_line(cx, cy)
    add_spot(PITCH_LENGTH / 2, PITCH_WIDTH / 2)
    
    # Penalty areas (18 x 44)
    add_line([0, 18, 18, 0], [18, 18, 62, 62])
    add_line([PITCH_LENGTH, PITCH_LENGTH - 18, PITCH_LENGTH - 18, PITCH_LENGTH], [18, 18, 62, 62])
    
    # Goal areas (6 x 20)
    add_line([0, 6, 6, 0], [30, 30, 50, 50])
    add_line([PITCH_LENGTH, PITCH_LENGTH - 6, PITCH_LENGTH - 6, PITCH_LENGTH], [30, 30, 50, 50])
    
    # Penalty spots
    add_spot(12, 40)
    add_spot(PITCH_LENGTH - 12, 40)
    
    # Penalty arcs ("D")
    ax, ay = arc_xy(12, 40, 10, -0.9273, 0.9273)
    add_line(ax, ay)
    ax, ay = arc_xy(PITCH_LENGTH - 12, 40, 10, 2.2143, 4.0689)
    add_line(ax, ay)
    
    # 3D goal frames (posts + crossbar + full netting)
    GH = 2.67   # goal height in yards (~8 ft)
    GW = 8.0    # goal width in yards (between posts = 44-36)
    GD = 2.5    # goal depth (how far the net extends back)

    def add_goal(side: str):
        """Add a fully detailed 3D goal structure (posts, crossbar, netting)."""
        # left post x-position: 0 for left goal, PITCH_LENGTH for right goal
        # goal y-range: 36 to 44
        if side == 'left':
            gx0 = 0       # goal line x
            gx1 = -GD     # back of net (behind the line)
        else:
            gx0 = PITCH_LENGTH
            gx1 = PITCH_LENGTH + GD

        gy0, gy1 = 36.0, 44.0   # left post, right post y-coords
        post_color = 'rgba(255, 255, 255, 1.0)'
        net_color_v = 'rgba(255, 255, 255, 0.22)'
        net_color_h = 'rgba(255, 255, 255, 0.14)'

        # ---- Posts & crossbar (front frame) ----
        # Left post
        fig.add_trace(go.Scatter3d(
            x=[gx0, gx0], y=[gy0, gy0], z=[0, GH],
            mode='lines', line=dict(color=post_color, width=8),
            hoverinfo='skip', showlegend=False))
        # Right post
        fig.add_trace(go.Scatter3d(
            x=[gx0, gx0], y=[gy1, gy1], z=[0, GH],
            mode='lines', line=dict(color=post_color, width=8),
            hoverinfo='skip', showlegend=False))
        # Crossbar
        fig.add_trace(go.Scatter3d(
            x=[gx0, gx0], y=[gy0, gy1], z=[GH, GH],
            mode='lines', line=dict(color=post_color, width=8),
            hoverinfo='skip', showlegend=False))

        # ---- Back frame ----
        # Left back post
        fig.add_trace(go.Scatter3d(
            x=[gx1, gx1], y=[gy0, gy0], z=[0, GH],
            mode='lines', line=dict(color='rgba(255,255,255,0.5)', width=4),
            hoverinfo='skip', showlegend=False))
        # Right back post
        fig.add_trace(go.Scatter3d(
            x=[gx1, gx1], y=[gy1, gy1], z=[0, GH],
            mode='lines', line=dict(color='rgba(255,255,255,0.5)', width=4),
            hoverinfo='skip', showlegend=False))
        # Back crossbar
        fig.add_trace(go.Scatter3d(
            x=[gx1, gx1], y=[gy0, gy1], z=[GH, GH],
            mode='lines', line=dict(color='rgba(255,255,255,0.5)', width=4),
            hoverinfo='skip', showlegend=False))

        # ---- Top connecting bars (front→back at post tops) ----
        for yy in [gy0, gy1]:
            fig.add_trace(go.Scatter3d(
                x=[gx0, gx1], y=[yy, yy], z=[GH, GH],
                mode='lines', line=dict(color='rgba(255,255,255,0.5)', width=4),
                hoverinfo='skip', showlegend=False))

        # ---- Bottom ground bars (front→back on ground) ----
        for yy in [gy0, gy1]:
            fig.add_trace(go.Scatter3d(
                x=[gx0, gx1], y=[yy, yy], z=[0.1, 0.1],
                mode='lines', line=dict(color='rgba(255,255,255,0.3)', width=3),
                hoverinfo='skip', showlegend=False))

        # ---- Vertical net strings (side panels + back) ----
        # Back panel: vertical strings
        vx, vy, vz = [], [], []
        for yy in np.linspace(gy0, gy1, 10):
            vx += [gx1, gx1, None]
            vy += [yy, yy, None]
            vz += [0, GH, None]
        # Side panels
        for side_y in [gy0, gy1]:
            for xx in np.linspace(gx0, gx1, 6):
                vx += [xx, xx, None]
                vy += [side_y, side_y, None]
                vz += [0, GH, None]
        fig.add_trace(go.Scatter3d(
            x=vx, y=vy, z=vz, mode='lines',
            line=dict(color=net_color_v, width=1),
            hoverinfo='skip', showlegend=False))

        # ---- Horizontal net strings (back panel) ----
        hx, hy, hz = [], [], []
        for zz in np.linspace(0.3, GH, 6):
            hx += [gx1, gx1, None]
            hy += [gy0, gy1, None]
            hz += [zz, zz, None]
        # Top net (roof) horizontal
        for xx in np.linspace(gx0, gx1, 6):
            hx += [xx, xx, None]
            hy += [gy0, gy1, None]
            hz += [GH - 0.05, GH - 0.05, None]
        fig.add_trace(go.Scatter3d(
            x=hx, y=hy, z=hz, mode='lines',
            line=dict(color=net_color_h, width=1),
            hoverinfo='skip', showlegend=False))

        # ---- Subtle glow highlight at goal mouth ----
        fig.add_trace(go.Scatter3d(
            x=[gx0], y=[(gy0 + gy1) / 2], z=[GH / 2],
            mode='markers',
            marker=dict(size=22, color='rgba(255,255,180,0.06)', symbol='circle'),
            hoverinfo='skip', showlegend=False))

    add_goal('left')
    add_goal('right')

    # Attacking-third highlight plane (gold, faint) + boundary line
    fig.add_trace(go.Mesh3d(
        x=[ATTACKING_THIRD_X, PITCH_LENGTH, PITCH_LENGTH, ATTACKING_THIRD_X],
        y=[0, 0, PITCH_WIDTH, PITCH_WIDTH],
        z=[0.30, 0.30, 0.30, 0.30],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color=THIRD_GOLD, opacity=0.12,
        name='Attacking Third (X > 80)', showlegend=False,
        hoverinfo='skip', flatshading=True
    ))
    add_line([ATTACKING_THIRD_X, ATTACKING_THIRD_X], [0, PITCH_WIDTH],
             color="rgba(251, 191, 36, 0.85)", width=4)

    import streamlit as st
    is_light = st.session_state.get('theme_mode', 'dark') == 'light'
    text_color = '#1e293b' if is_light else 'white'
    legend_bg = 'rgba(255, 255, 255, 0.8)' if is_light else 'rgba(15, 23, 42, 0.65)'
    legend_border = 'rgba(0, 0, 0, 0.1)' if is_light else 'rgba(255, 255, 255, 0.18)'

    # --- Scene / camera ---
    fig.update_layout(
        height=680,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Poppins", color=text_color),
        scene=dict(
            xaxis=dict(range=[-6, PITCH_LENGTH + 6], visible=False),
            yaxis=dict(range=[-6, PITCH_WIDTH + 6], visible=False),
            zaxis=dict(range=[0, 14], visible=False),
            aspectmode='manual',
            aspectratio=dict(x=1.5, y=1.0, z=0.18),
            camera=dict(
                up=dict(x=0, y=0, z=1),
                **CAMERA_PRESETS.get(camera_preset, CAMERA_PRESETS["🚁 Aerial"])
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        legend=dict(
            bgcolor=legend_bg,
            bordercolor=legend_border,
            borderwidth=1,
            font=dict(color=text_color, size=12),
            orientation="h",
            yanchor="bottom", y=0.0,
            xanchor="center", x=0.5
        )
    )
    return fig


# ===========================================================================
# 2D Pitch Visualization
# ===========================================================================

def create_soccer_pitch() -> go.Figure:
    """
    Create a Plotly 2D figure with a modern soccer pitch background.
    
    Returns
    -------
    go.Figure
        Plotly 2D figure with pitch markings
    """
    fig = go.Figure()

    # Pitch base - only border, no fill so Voronoi cells are vibrant like 3D
    fig.add_shape(
        type="rect", x0=0, y0=0, x1=PITCH_LENGTH, y1=PITCH_WIDTH,
        line=dict(color=LINE_COLOR, width=3),
        fillcolor="rgba(16, 110, 55, 0)"  # Transparent - no green fill
    )
    
    # Center line + circle + spot
    fig.add_shape(
        type="line",
        x0=PITCH_LENGTH / 2, y0=0,
        x1=PITCH_LENGTH / 2, y1=PITCH_WIDTH,
        line=dict(color=LINE_COLOR, width=3)
    )
    fig.add_shape(
        type="circle",
        x0=PITCH_LENGTH / 2 - 10, y0=PITCH_WIDTH / 2 - 10,
        x1=PITCH_LENGTH / 2 + 10, y1=PITCH_WIDTH / 2 + 10,
        line=dict(color=LINE_COLOR, width=3)
    )
    fig.add_shape(
        type="circle",
        x0=PITCH_LENGTH / 2 - 0.5, y0=PITCH_WIDTH / 2 - 0.5,
        x1=PITCH_LENGTH / 2 + 0.5, y1=PITCH_WIDTH / 2 + 0.5,
        fillcolor="white", line=dict(color="white", width=0)
    )
    
    # Penalty + goal areas
    fig.add_shape(
        type="rect",
        x0=0, y0=PITCH_WIDTH / 2 - 22,
        x1=18, y1=PITCH_WIDTH / 2 + 22,
        line=dict(color=LINE_COLOR, width=3)
    )
    fig.add_shape(
        type="rect",
        x0=PITCH_LENGTH - 18, y0=PITCH_WIDTH / 2 - 22,
        x1=PITCH_LENGTH, y1=PITCH_WIDTH / 2 + 22,
        line=dict(color=LINE_COLOR, width=3)
    )
    fig.add_shape(
        type="rect",
        x0=0, y0=PITCH_WIDTH / 2 - 10,
        x1=6, y1=PITCH_WIDTH / 2 + 10,
        line=dict(color=LINE_COLOR, width=3)
    )
    fig.add_shape(
        type="rect",
        x0=PITCH_LENGTH - 6, y0=PITCH_WIDTH / 2 - 10,
        x1=PITCH_LENGTH, y1=PITCH_WIDTH / 2 + 10,
        line=dict(color=LINE_COLOR, width=3)
    )
    
    # Penalty spots
    fig.add_shape(
        type="circle",
        x0=11.5, y0=PITCH_WIDTH / 2 - 0.5,
        x1=12.5, y1=PITCH_WIDTH / 2 + 0.5,
        fillcolor="white", line=dict(color="white", width=0)
    )
    fig.add_shape(
        type="circle",
        x0=PITCH_LENGTH - 12.5, y0=PITCH_WIDTH / 2 - 0.5,
        x1=PITCH_LENGTH - 11.5, y1=PITCH_WIDTH / 2 + 0.5,
        fillcolor="white", line=dict(color="white", width=0)
    )

    # Attacking-third line
    fig.add_shape(
        type="line",
        x0=ATTACKING_THIRD_X, y0=0,
        x1=ATTACKING_THIRD_X, y1=PITCH_WIDTH,
        line=dict(color="rgba(251, 191, 36, 0.85)", width=3, dash="dash")
    )

    import streamlit as st
    is_light = st.session_state.get('theme_mode', 'dark') == 'light'
    text_color = '#1e293b' if is_light else 'white'
    legend_bg = 'rgba(255, 255, 255, 0.8)' if is_light else 'rgba(15, 23, 42, 0.6)'
    legend_border = 'rgba(0, 0, 0, 0.1)' if is_light else 'rgba(255, 255, 255, 0.2)'

    fig.update_layout(
        showlegend=True,
        plot_bgcolor='rgba(20, 30, 48, 1)',  # Dark background like 3D
        paper_bgcolor='rgba(0, 0, 0, 0)',
        height=620,
        xaxis=dict(
            range=[0, PITCH_LENGTH],
            showgrid=False,
            zeroline=False,
            title=dict(text="Length (yards)", font=dict(color=text_color, size=14, family="Poppins")),
            tickfont=dict(color=text_color),
            constrain='domain'
        ),
        yaxis=dict(
            range=[0, PITCH_WIDTH],
            showgrid=False,
            zeroline=False,
            title=dict(text="Width (yards)", font=dict(color=text_color, size=14, family="Poppins")),
            tickfont=dict(color=text_color),
            scaleanchor="x",
            scaleratio=1,
            constrain='domain'
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(family="Poppins", color=text_color),
        legend=dict(
            bgcolor=legend_bg,
            bordercolor=legend_border,
            borderwidth=1,
            font=dict(color=text_color, size=12)
        )
    )
    return fig

# Made with Bob

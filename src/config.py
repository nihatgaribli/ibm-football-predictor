"""
Configuration and Constants for Soccer Tactical Analysis Application

This module contains all configuration constants, color schemes, and camera presets
used throughout the application.
"""

# ===========================================================================
# Pitch Dimensions
# ===========================================================================
PITCH_LENGTH = 120
PITCH_WIDTH = 80
ATTACKING_THIRD_X = 80

# ===========================================================================
# Color Palette
# ===========================================================================
# Team colors (consistent between 2D and 3D views)
ATTACK_HEX = "#2E9BFF"           # electric blue
ATTACK_FILL = "rgba(46, 155, 255, 0.45)"
DEFEND_HEX = "#FF4D5E"           # vivid coral red
DEFEND_FILL = "rgba(255, 77, 94, 0.42)"
GK_HEX = "#FBBF24"               # gold for goalkeepers
LINE_COLOR = "rgba(255, 255, 255, 0.85)"
THIRD_GOLD = "#FBBF24"

# Shot outcome colors
OUTCOME_COLORS = {
    'Goal': '#10b981',
    'Saved': '#38bdf8',
    'Off T': '#f59e0b',
    'Blocked': '#ef4444',
    'Wayward': '#94a3b8',
    'Post': '#a855f7',
}

# ===========================================================================
# 3D Camera Presets
# ===========================================================================
# Plotly scene.camera.eye settings, tuned for aspectratio 1.5:1:0.18
CAMERA_PRESETS = {
    "🚁 Aerial": dict(
        eye=dict(x=0.25, y=-1.45, z=1.5),
        center=dict(x=0, y=0, z=-0.05)
    ),
    "📺 Broadcast": dict(
        eye=dict(x=1.55, y=-1.5, z=1.0),
        center=dict(x=0, y=0, z=-0.05)
    ),
    "🥅 Behind Goal": dict(
        eye=dict(x=2.05, y=-0.15, z=0.62),
        center=dict(x=0.1, y=0, z=-0.02)
    ),
    "🗺️ Top-Down": dict(
        eye=dict(x=0.0, y=-0.05, z=2.15),
        center=dict(x=0, y=0, z=0)
    ),
}

# ===========================================================================
# UI Configuration
# ===========================================================================
PAGE_CONFIG = {
    'page_title': "Soccer Tactical Analysis",
    'page_icon': "⚽",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
}

# Made with Bob

# ⚽ Soccer Tactical Analysis

An interactive web application for analyzing soccer tracking data using Voronoi diagrams and AI-powered tactical insights.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Overview

This project provides a comprehensive toolkit for soccer tactical analysis, combining:
- **Tracking Data Extraction** from StatsBomb's freeze-frame data
- **Voronoi Spatial Analysis** for zone dominance calculation
- **AI-Powered Tactical Explanations** using IBM Granite LLM
- **Interactive Web Interface** built with Streamlit

## ✨ Features

- 📊 **Real-time Voronoi Diagrams** - Visualize spatial control on the pitch (2D & 3D Interactive)
- ⚖️ **Side-by-Side Shot Comparison** - Compare two different shots with synchronized maps and metrics
- 🎨 **Premium UI/UX** - Glassmorphism design, dynamic Light/Dark mode, and responsive layout
- 🎯 **Zone Dominance Metrics** - Calculate team control in attacking third
- 🤖 **AI Tactical Insights** - Get intelligent explanations of spatial patterns
- 📈 **Interactive Dashboard** - Explore matches and shot events with ease

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/soccer-tactical-analysis.git
cd soccer-tactical-analysis
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Launch the Streamlit web app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📦 Project Structure

```
soccer-tactical-analysis/
├── app.py                          # Main Streamlit application
├── soccer_tracking_data.py         # Tracking data extraction module
├── spatial_analysis.py             # Voronoi spatial analysis module
├── tactical_explainer.py           # AI tactical explanation module
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── STREAMLIT_APP_README.md         # Detailed app documentation
├── SPATIAL_ANALYSIS_README.md      # Spatial analysis guide
└── TACTICAL_EXPLAINER_README.md    # AI explainer documentation
```

## 🔧 Core Modules

### 1. Tracking Data Extraction (`soccer_tracking_data.py`)

Extract player positions from StatsBomb freeze-frame data:

```python
from soccer_tracking_data import get_soccer_tracking_data

# Fetch tracking data for a match
tracking_df = get_soccer_tracking_data(match_id=3869151)
```

**Output DataFrame columns:**
- `shot_id` - Unique shot identifier
- `timestamp` - Event timestamp
- `player_name` - Player name
- `team_name` - Team (Teammate/Opponent)
- `x`, `y` - Player coordinates
- `is_goalkeeper` - Goalkeeper flag

### 2. Spatial Analysis (`spatial_analysis.py`)

Compute Voronoi diagrams and zone dominance:

```python
from spatial_analysis import SoccerVoronoiAnalyzer

analyzer = SoccerVoronoiAnalyzer()
results = analyzer.analyze_multiple_shots(tracking_df)
summary = analyzer.get_summary_statistics(results)
```

**Key Metrics:**
- Bounded Voronoi cells (120x80 yard pitch)
- Player-level controlled area
- Team dominance in attacking third (X > 80)
- Total pitch coverage percentage

### 3. Tactical Explainer (`tactical_explainer.py`)

Generate AI-powered tactical insights:

```python
from tactical_explainer import TacticalExplainer

explainer = TacticalExplainer()
explanation = explainer.generate_explanation(analysis_result)
```

## 📊 Example Analysis Output

```
Shot ID: 9fd07a9a-2de2-4ba5-b400-6a2264835ba2
Total Pitch Coverage: 78.97%

Team Dominance in Attacking Third (X > 80):
  Attacking Team: 38.26%
  Defending Team: 61.74%

AI Tactical Insight:
The defending team has established strong spatial control in the 
attacking third (61.74%), creating a compact defensive block that 
limits attacking space...
```

## 🎨 Web Application Features

- **Interactive Pitch Visualization** - Click and explore Voronoi cells
- **Shot Selection Dropdown** - Analyze any shot event in the match
- **Real-time Metrics Dashboard** - Live updates of dominance metrics
- **AI Tactical Analysis** - Contextual explanations for each shot
- **Player Area Rankings** - See which players control the most space

## 📚 Documentation

- **[Streamlit App Guide](STREAMLIT_APP_README.md)** - Complete app documentation
- **[Spatial Analysis Guide](SPATIAL_ANALYSIS_README.md)** - Voronoi analysis details
- **[Tactical Explainer Guide](TACTICAL_EXPLAINER_README.md)** - AI integration guide

## 🛠️ Requirements

- Python 3.7+
- pandas >= 1.3.0
- statsbombpy >= 1.0.0
- numpy >= 1.21.0
- scipy >= 1.7.0
- shapely >= 1.8.0
- streamlit >= 1.28.0
- plotly >= 5.14.0
- langchain-ibm >= 0.1.0 (optional, for AI features)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is provided as-is for educational and research purposes.

## 🙏 Acknowledgments

- **StatsBomb** - For providing open soccer data
- **IBM Granite** - For AI-powered tactical insights
- **Streamlit** - For the amazing web framework

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with using Python, Streamlit, and IBM Granite AI**

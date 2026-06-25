# 🚀 Application Setup and Run Instructions

## 1️⃣ Create Virtual Environment (Recommended)

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

## 2️⃣ Install Required Packages

```bash
pip install -r requirements.txt
```

## 3️⃣ Run the Application

```bash
streamlit run app.py
```

## 4️⃣ Open in Browser

The application will automatically open in your browser. If it doesn't, navigate to the URL shown in the terminal (typically: `http://localhost:8501`)

---

## 📁 Project Structure

```
agents-appshyde-changes-update/
│
├── app.py                          # Main application file
├── requirements.txt                # Python dependencies
├── README.md                       # Project information
│
└── src/                            # Source code modules
    ├── config.py                   # Configuration and constants
    ├── ui_components.py            # UI components and CSS
    ├── pitch_visualization.py      # Pitch visualization functions
    ├── voronoi_visualization.py    # Voronoi diagram functions
    ├── data_loader.py              # Data loading functions
    ├── soccer_tracking_data.py     # StatsBomb data integration
    ├── spatial_analysis.py         # Spatial analysis algorithms
    └── tactical_explainer.py       # AI tactical explanations
```

---

## 🔧 Troubleshooting

### Issue: `ModuleNotFoundError`
**Solution:** 
```bash
pip install -r requirements.txt
```

### Issue: Port already in use
**Solution:**
```bash
streamlit run app.py --server.port 8502
```

### Issue: StatsBomb data not loading
**Solution:** Check your internet connection and try again

---

## 💡 Usage Instructions

1. **Match Selection:** Choose a World Cup match from the left sidebar
2. **Visualization Mode:** Select between 3D Interactive or 2D Classic view
3. **Camera Angle:** Change camera perspective in 3D mode
4. **Shot Analysis:** Select a shot to view spatial control analysis
5. **AI Insights:** Read tactical explanations and insights

---

## 🎨 Features

✅ 3D and 2D Voronoi visualization
✅ AI-powered tactical explanations
✅ Shot map and timeline analysis
✅ Light/Dark theme support
✅ Interactive camera controls
✅ Real-time spatial analysis

---

## 📞 Support

If you encounter issues:
1. Ensure virtual environment is activated
2. Verify all packages are installed
3. Confirm Python version is 3.8+

**Good luck! ⚽**
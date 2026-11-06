# Health AI Risk Monitor
Monitoring-first Streamlit app focused on **what is new in Health AI risk**.

## VS Code test
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python monitor.py
streamlit run app.py
```

There is no dummy dataset. `monitor.py` must collect real public-web records before the app starts.

## Deploy
Push this folder to GitHub. Run the included **Refresh Health AI Risk Monitor** Action once manually, then deploy `app.py` on Streamlit Community Cloud. The scheduled workflow runs every six hours and commits the deduplicated monitoring dataset.

## Views
- What's New: 24h/7d/30d first-seen monitoring
- Risk Watch
- Regulatory Watch
- Health Conditions
- Explore Signals
- Publication/release date filter
- Clickable sources

All automated results are research signals pending human review.

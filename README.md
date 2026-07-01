# Movie Industry Intelligence Streamlit App

This project turns the supplied `movies.csv` dataset and `movies_analysis.ipynb` analysis into an interactive Streamlit reporting app.

## What is included

- Sidebar filters for year, genre, rating, country, and minimum IMDb score
- Overview dashboard with KPI cards, yearly trend, genre mix, and top movie rankings
- Exploratory analysis with distributions and outlier watchlist
- Financial intelligence views for genre ROI, budget tiers, and profit vs score
- Spearman/Pearson correlation heatmaps and ranked relationship tables
- Data explorer with search, filtered CSV download, and Markdown report export

## Run locally

```powershell
cd C:\Users\asus\Documents\Codex\2026-07-01\u\outputs\movies_streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

The app expects the dataset at:

```text
data/movies.csv
```

That CSV has already been copied into this project folder.

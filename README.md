# Zomato Streamlit Dashboard

Interactive Streamlit dashboard for exploring Zomato restaurant CSV files.

## Features

- Upload CSV or provide local path
- Interactive filters: City, Cuisine, Rating range, Price range, Table booking, Online delivery
- Charts: top cities, popular cuisines, rating distribution, cost histogram
- Folium map with clustered markers
- Download filtered CSV
- Robust CSV encoding and delimiter detection

## Quick start

1. Create a virtual environment and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS / Linux
   venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   streamlit run app.py
   ```

## Advanced analytics included
- Price vs rating scatter (added to app)
- City-wise summary (top cities by average rating and restaurant counts)
- Cuisine trend summaries

## Next steps / Universal CSV Analyzer
A separate universal CSV analyzer project will follow; it will auto-detect column types and generate tailored EDA for any CSV.

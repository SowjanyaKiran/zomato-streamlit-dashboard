import io
from typing import Optional
import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from utils import load_zomato_csv, clean_zomato_df

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(page_title="Zomato Data Analyzer", layout="wide")

st.title("Zomato Data Analyzer — Interactive Dashboard")
st.markdown("Upload your Zomato CSV (or enter a path). Use the sidebar to filter and explore data.")

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------
st.sidebar.header("Data Input")

uploaded_file = st.sidebar.file_uploader("Upload Zomato CSV", type=["csv"])
file_path_input = st.sidebar.text_input("Or enter CSV path (local)", "")

df: Optional[pd.DataFrame] = None

if uploaded_file is not None:
    try:
        df = load_zomato_csv(uploaded_file)
    except Exception as e:
        st.sidebar.error(f"Failed to read uploaded CSV: {e}")

elif file_path_input.strip():
    try:
        df = load_zomato_csv(file_path_input.strip())
    except Exception as e:
        st.sidebar.error(f"Failed to read CSV: {e}")

# STOP APP IF NO DATA LOADED
if df is None:
    st.info("Please upload a CSV file or enter a valid path.")
    st.stop()

# -------------------------------------------------------
# CLEAN DATA
# -------------------------------------------------------
df = clean_zomato_df(df)
st.sidebar.success("Data loaded and cleaned.")

# -------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------
st.sidebar.header("Filters")

# City filter
cities = sorted(df["City"].dropna().astype(str).unique().tolist())
selected_cities = st.sidebar.multiselect("City", options=cities, default=[])

# Cuisine filter
all_cuisines_series = df["Cuisines"].dropna().astype(str).str.split(",")
flat_cuisines = sorted({c.strip() for row in all_cuisines_series for c in row if c.strip()})
selected_cuisines = st.sidebar.multiselect("Cuisines", options=flat_cuisines, default=[])

# Rating range
min_rating = float(df["Aggregate rating"].min())
max_rating = float(df["Aggregate rating"].max())
rating_range = st.sidebar.slider("Aggregate Rating", min_value=min_rating, max_value=max_rating, value=(min_rating, max_rating))

# Price range
if "Price range" in df.columns:
    pr_min = int(df["Price range"].min())
    pr_max = int(df["Price range"].max())
    price_range = st.sidebar.slider("Price range", min_value=pr_min, max_value=pr_max, value=(pr_min, pr_max))
else:
    price_range = None

table_booking = st.sidebar.selectbox("Has Table Booking", ["Both", "Yes", "No"])
online_delivery = st.sidebar.selectbox("Has Online Delivery", ["Both", "Yes", "No"])

# -------------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------------
mask = pd.Series(True, index=df.index)

if selected_cities:
    mask &= df["City"].isin(selected_cities)

if selected_cuisines:
    def cuisine_match(cell):
        cell_cuisines = [c.strip().lower() for c in str(cell).split(",")]
        return any(sc.lower() in cell_cuisines for sc in selected_cuisines)
    mask &= df["Cuisines"].apply(cuisine_match)

mask &= df["Aggregate rating"].between(rating_range[0], rating_range[1])

if price_range:
    mask &= df["Price range"].between(price_range[0], price_range[1])

if table_booking != "Both":
    mask &= df["Has Table booking"].astype(str).str.lower() == table_booking.lower()

if online_delivery != "Both":
    mask &= df["Has Online delivery"].astype(str).str.lower() == online_delivery.lower()

filtered = df[mask].copy()

st.sidebar.markdown(f"**Filtered rows:** {len(filtered):,}")

# -------------------------------------------------------
# METRICS
# -------------------------------------------------------
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Top-level Metrics")
    a, b, c = st.columns(3)
    a.metric("Restaurants", len(filtered))
    b.metric("Avg Rating", round(filtered["Aggregate rating"].mean(), 2) if len(filtered) else "N/A")
    c.metric("Avg Cost for Two", round(filtered["Average Cost for two"].mean(), 2) if len(filtered) else "N/A")

with col2:
    st.subheader("Download Filtered CSV")
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="zomato_filtered.csv", mime="text/csv")

st.markdown("---")

# -------------------------------------------------------
# CHARTS
# -------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Top Cities")
    city_counts = filtered["City"].value_counts().nlargest(10).reset_index()
    city_counts.columns = ["City", "Count"]
    st.plotly_chart(px.bar(city_counts, x="City", y="Count"))

with right:
    st.subheader("Top Cuisines")
    cuisine_explode = filtered["Cuisines"].dropna().astype(str).str.split(",").explode().str.strip()
    top_cuisines = cuisine_explode.value_counts().nlargest(12).reset_index()
    top_cuisines.columns = ["Cuisine", "Count"]
    st.plotly_chart(px.bar(top_cuisines, x="Cuisine", y="Count"))

st.markdown("---")

st.subheader("Rating Distribution")
st.plotly_chart(px.histogram(filtered, x="Aggregate rating", nbins=20))

st.subheader("Average Cost for Two Distribution")
st.plotly_chart(px.histogram(filtered, x="Average Cost for two", nbins=30))

st.markdown("---")

# -------------------------------------------------------
# MAP
# -------------------------------------------------------
st.subheader("Restaurant Locations Map")

if "Latitude" in filtered.columns and "Longitude" in filtered.columns:
    valid_map_df = filtered.dropna(subset=["Latitude", "Longitude"])

    if len(valid_map_df):
        m = folium.Map(location=[valid_map_df["Latitude"].mean(), valid_map_df["Longitude"].mean()], zoom_start=5)
        mc = MarkerCluster()

        for _, row in valid_map_df.iterrows():
            folium.Marker(
                [row["Latitude"], row["Longitude"]],
                popup=f"<b>{row['Restaurant Name']}</b><br>{row['City']}<br>Rating: {row['Aggregate rating']}<br>Cuisines: {row['Cuisines']}"
            ).add_to(mc)

        mc.add_to(m)
        st_folium(m, width=900, height=500)
    else:
        st.info("No valid coordinates for map.")
else:
    st.info("Latitude/Longitude columns missing.")

st.markdown("---")

# -------------------------------------------------------
# DATA PREVIEW
# -------------------------------------------------------
st.subheader("Filtered Data Preview")
st.dataframe(filtered.head(200))

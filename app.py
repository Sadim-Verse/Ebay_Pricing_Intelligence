import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress

# CONSTANTS
REFERENCE_YEAR = 2016
LOW_COUNT_THRESHOLD = 5

# Mileage bins (same as in notebook)
MILEAGE_BINS = [0, 50000, 100000, 150000, 200000, 500001]
MILEAGE_LABELS = ['0-50k', '50k-100k', '100k-150k', '150k-200k', '200k+']

# DATA LOADING & PREPROCESSING (cached)
@st.cache_data
def load_and_clean_data():
    # Load
    data = pd.read_csv('autos.csv', encoding='latin-1')
    
    # Rename columns
    column_mapping = {
        'dateCrawled': 'date_crawled', 'name': 'name', 'seller': 'seller',
        'offerType': 'offer_type', 'price': 'price', 'abtest': 'ab_test',
        'vehicleType': 'vehicle_type', 'yearOfRegistration': 'registration_year',
        'gearbox': 'gearbox', 'powerPS': 'power_ps', 'model': 'model',
        'odometer': 'odometer_km', 'monthOfRegistration': 'registration_month',
        'fuelType': 'fuel_type', 'brand': 'brand',
        'notRepairedDamage': 'unrepaired_damage',
        'dateCreated': 'date_created', 'nrOfPictures': 'num_pictures',
        'postalCode': 'postal_code', 'lastSeen': 'last_seen'
    }
    data.rename(columns=column_mapping, inplace=True)
    
    # Type conversions
    date_cols = ['date_crawled', 'last_seen', 'date_created']
    for col in date_cols:
        data[col] = pd.to_datetime(data[col], errors='coerce')
    data['price'] = data['price'].str[1:].str.replace(',', '', regex=False).astype(int)
    data['odometer_km'] = data['odometer_km'].str.replace('km', '').str.replace(',', '').astype(int)
    
    # Drop irrelevant columns
    drop_cols = ['num_pictures', 'date_crawled', 'last_seen', 'date_created',
                 'ab_test', 'postal_code', 'name', 'model', 'offer_type']
    data.drop(columns=drop_cols, inplace=True, errors='ignore')
    
    # Fill missing values with 'unknown'
    data.fillna({
        'vehicle_type': 'unknown',
        'gearbox': 'unknown',
        'fuel_type': 'unknown',
        'unrepaired_damage': 'unknown'
    }, inplace=True)
    
    # Encode categories
    cat_cols = ['seller', 'vehicle_type', 'gearbox', 'fuel_type', 'brand', 'unrepaired_damage']
    for col in cat_cols:
        data[col] = data[col].astype('category')
    data['seller'] = data['seller'].cat.rename_categories({'privat': 'private', 'gewerblich': 'commercial'})
    data['vehicle_type'] = data['vehicle_type'].cat.rename_categories(
        {'kleinwagen': 'smallcar', 'cabrio': 'convertible', 'andere': 'other'})
    data['gearbox'] = data['gearbox'].cat.rename_categories({'manuell': 'manually', 'automatik': 'automatic'})
    data['unrepaired_damage'] = data['unrepaired_damage'].cat.rename_categories({'nein': 'no', 'ja': 'yes'})
    data['fuel_type'] = data['fuel_type'].cat.rename_categories({'elektro': 'electro', 'andere': 'other'})
    
    # Derive car_age
    data['car_age'] = REFERENCE_YEAR - data['registration_year']
    
    # Outlier removal
    data_clean = data[
        (data['price'] >= 500) & (data['price'] <= 250_000) &
        (data['registration_year'] >= 1950) &
        (data['registration_year'] <= REFERENCE_YEAR) &
        (data['car_age'] >= 0) &
        (data['odometer_km'] >= 0) & (data['odometer_km'] <= 500_000) &
        (data['power_ps'] > 0) & (data['power_ps'] <= 1000)
    ].copy()
    
    # Add mileage bin
    data_clean['mileage_bin'] = pd.cut(
        data_clean['odometer_km'],
        bins=MILEAGE_BINS,
        labels=MILEAGE_LABELS,
        right=False
    )
    
    return data_clean

# BUILD LOOKUP TABLES (cached)
@st.cache_data
def build_lookup_tables(data_clean):
    # Detailed lookup (brand, age, mileage bin)
    price_lookup = (
        data_clean.groupby(['brand', 'car_age', 'mileage_bin'], observed=True)['price']
        .agg(
            median_price='median',
            q1_price=lambda x: x.quantile(0.25),
            q3_price=lambda x: x.quantile(0.75),
            count='count'
        )
        .reset_index()
    )
    price_lookup = price_lookup[price_lookup['count'] > 0].reset_index(drop=True)
    
    # Brand-level fallback
    brand_stats = (
        data_clean.groupby('brand', observed=True)['price']
        .agg(
            median_price='median',
            q1_price=lambda x: x.quantile(0.25),
            q3_price=lambda x: x.quantile(0.75),
            count='count'
        )
        .reset_index()
    )
    
    # Overall market
    overall_q1 = data_clean['price'].quantile(0.25)
    overall_med = data_clean['price'].median()
    overall_q3 = data_clean['price'].quantile(0.75)
    overall_n = len(data_clean)
    
    return price_lookup, brand_stats, overall_q1, overall_med, overall_q3, overall_n

# DEPRECIATION ANALYSIS (cached)
@st.cache_data
def compute_depreciation_rates(data_clean):
    brand_age = data_clean.groupby(['brand', 'car_age'], observed=True)['price'].median().reset_index()
    MIN_AGE_POINTS = 10
    MIN_R2 = 0.30
    annual_rates = {}
    r2_values = {}
    for brand, grp in brand_age.dropna(subset=['price']).groupby('brand', observed=True):
        grp = grp[grp['car_age'] >= 0]
        if len(grp) < MIN_AGE_POINTS:
            continue
        x = grp['car_age'].values
        y = np.log(grp['price'].values)
        slope, _, r, _, _ = linregress(x, y)
        r2 = r ** 2
        if r2 < MIN_R2:
            continue
        annual_rates[brand] = -slope
        r2_values[brand] = r2
    rates_df = pd.DataFrame({'annual_rate': annual_rates, 'r2': r2_values}).sort_values('annual_rate')
    rates_df['annual_pct'] = rates_df['annual_rate'] * 100
    return rates_df

# PRICE PREDICTION FUNCTION
def mileage_label(mileage: float) -> str:
    for i in range(len(MILEAGE_BINS) - 1):
        if MILEAGE_BINS[i] <= mileage < MILEAGE_BINS[i+1]:
            return MILEAGE_LABELS[i]
    return MILEAGE_LABELS[-1]

def predict_price_range(brand: str, mileage: float, age: int,
                        lookup, brand_stats,
                        overall_q1, overall_med, overall_q3, overall_n):
    brand_lower = brand.lower().strip()
    bin_label = mileage_label(mileage)
    
    # Normalise brand column
    lookup_brands = lookup['brand'].astype(str).str.lower()
    
    # Level 1: exact match
    mask1 = (lookup_brands == brand_lower) & (lookup['car_age'] == age) & (lookup['mileage_bin'].astype(str) == bin_label)
    m1 = lookup[mask1]
    if not m1.empty:
        row = m1.iloc[0]
        warn = f"Low sample count ({int(row['count'])} records) — estimate uncertain." if row['count'] < LOW_COUNT_THRESHOLD else ""
        return {
            'q1': row['q1_price'], 'median': row['median_price'], 'q3': row['q3_price'],
            'count': int(row['count']), 'fallback_level': 1, 'warning': warn
        }
    
    # Level 2: brand + mileage bin, closest age
    mask2 = (lookup_brands == brand_lower) & (lookup['mileage_bin'].astype(str) == bin_label)
    m2 = lookup[mask2].copy()
    if not m2.empty:
        m2['age_diff'] = (m2['car_age'] - age).abs()
        row = m2.sort_values('age_diff').iloc[0]
        warn = f"Approximate match: closest age in lookup is {int(row['car_age'])} yr. "
        if row['count'] < LOW_COUNT_THRESHOLD:
            warn += f"Low sample count ({int(row['count'])}) — estimate uncertain."
        return {
            'q1': row['q1_price'], 'median': row['median_price'], 'q3': row['q3_price'],
            'count': int(row['count']), 'fallback_level': 2, 'warning': warn
        }
    
    # Level 3: brand-only
    bs_brands = brand_stats['brand'].astype(str).str.lower()
    mask3 = bs_brands == brand_lower
    m3 = brand_stats[mask3]
    if not m3.empty:
        row = m3.iloc[0]
        warn = "Only brand-level estimate available (mileage/age ignored). Treat with caution."
        return {
            'q1': row['q1_price'], 'median': row['median_price'], 'q3': row['q3_price'],
            'count': int(row['count']), 'fallback_level': 3, 'warning': warn
        }
    
    # Level 4: overall market
    return {
        'q1': overall_q1, 'median': overall_med, 'q3': overall_q3,
        'count': overall_n, 'fallback_level': 4,
        'warning': "Brand not found in dataset. Returning overall market medians."
    }

# STREAMLIT UI
st.set_page_config(page_title="Car Price Intelligence Tool", layout="wide")
st.title("🚗 eBay Kleinanzeigen – Used Car Pricing Tool")
st.markdown("""
**What this tool does:**  
Given a car's **brand**, **age** (years), and **mileage**, we return an expected price range (25th–50th–75th percentiles) based on real marketplace data from `autos.csv`.  
The tool uses a three‑level fallback: exact (brand+age+mileage bin) → nearest age → brand‑only → whole market.
""")

# Load data
with st.spinner("Loading data and building models..."):
    data_clean = load_and_clean_data()
    price_lookup, brand_stats, overall_q1, overall_med, overall_q3, overall_n = build_lookup_tables(data_clean)
    rates_df = compute_depreciation_rates(data_clean)

# Sidebar inputs
st.sidebar.header("🔍 Car Parameters")
brand_input = st.sidebar.text_input("Brand", value="volkswagen")
age_input = st.sidebar.number_input("Age (years)", min_value=0, max_value=50, value=5, step=1)
mileage_input = st.sidebar.number_input("Mileage (km)", min_value=0, max_value=500_000, value=80_000, step=5000)

if st.sidebar.button("Estimate Price", type="primary"):
    result = predict_price_range(
        brand_input, mileage_input, age_input,
        price_lookup, brand_stats,
        overall_q1, overall_med, overall_q3, overall_n
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Lower bound (Q1)", f"€{result['q1']:,.0f}")
    col2.metric("📊 Median price", f"€{result['median']:,.0f}")
    col3.metric("💎 Upper bound (Q3)", f"€{result['q3']:,.0f}")
    st.caption(f"Based on {result['count']} comparable listings | Fallback level: {result['fallback_level']}")
    if result['warning']:
        st.warning(result['warning'])

# Tabs for additional insights
tab1, tab2 = st.tabs(["📉 Brand Depreciation Rates", "📈 Price vs. Age Curve"])

with tab1:
    st.subheader("Annual Depreciation Rate by Brand (Log‑Linear Regression)")
    if not rates_df.empty:
        rates_df_display = rates_df[['annual_pct', 'r2']].rename(
            columns={'annual_pct': 'Annual Depreciation (%)', 'r2': 'R²'})
        st.dataframe(rates_df_display, use_container_width=True)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(range(len(rates_df)), rates_df['annual_pct'],
                      color=['green' if v < 5 else 'orange' if v < 10 else 'red'
                             for v in rates_df['annual_pct']])
        ax.set_xticks(range(len(rates_df)))
        ax.set_xticklabels(rates_df.index, rotation=45, ha='right')
        ax.set_ylabel('Annual Depreciation (%)')
        ax.set_title('Annual Depreciation Rate (higher = faster value loss)')
        st.pyplot(fig)
        st.caption("Green: <5% per year (best retention)  |  Orange: 5‑10%  |  Red: >10% (fastest drop)")
    else:
        st.info("Not enough reliable regressions (need ≥10 age points and R²≥0.30).")

with tab2:
    st.subheader("Median Price vs. Vehicle Age (All Brands)")
    age_median = data_clean.groupby('car_age')['price'].median().reset_index()
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(age_median['car_age'], age_median['price'], marker='o', color='steelblue', linewidth=2)
    ax.set_xlabel('Vehicle Age (years)')
    ax.set_ylabel('Median Price (EUR)')
    ax.set_title('Typical Depreciation Curve')
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)
    st.caption("Steep drop in first 5 years, then slower linear decline. Spike after ~25 years is survivor bias (collector cars).")
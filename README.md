# 🚗 eBay Kleinanzeigen – Used Car Market Intelligence & Pricing Tool

**Python · Pandas · Streamlit · Matplotlib · Seaborn**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url-here.streamlit.app/)  
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📊 Executive Summary

The secondary automotive market is notoriously fragmented, with individual sellers listing vehicles using inconsistent data, placeholder prices, and incomplete metadata. This project transforms raw eBay Kleinanzeigen listing data into **actionable pricing intelligence**.

We built a complete **data engineering pipeline** that cleans 50,000 raw listings, removes 10,241 erroneous records (20.5%), and reduces price skewness from an unusable 184.91 to a realistic 5.73.  
Through **exploratory data analysis** we quantify the true drivers of depreciation: brand positioning (Porsche commands 3–5× higher median prices than volume brands), mileage (explains ~17% of price variance), and vehicle age (steepest drop in first 5 years).

Finally, we deploy a **deterministic pricing estimator** – a transparent, interpretable tool that returns Q1, median, and Q3 prices based on brand, age, and mileage. The tool uses a 4‑level fallback system and is embedded in an interactive **Streamlit dashboard**, enabling dealers, resellers, and platforms to make data‑driven pricing decisions in real time.

**Live Application:** [https://ebay-auto-pricing-estimator-demo.streamlit.app/](https://ebay-auto-pricing-estimator-demo.streamlit.app/) (replace with actual URL)

---

## 🛠️ Data Engineering

Real‑world marketplace data is messy. To build reliable benchmarks, we implemented a rigorous multi‑step cleaning pipeline.

### 1. Structural Cleaning & Localization

- **Column renaming:** Translated German column names (`yearOfRegistration` → `registration_year`) and converted to snake_case.
- **Type casting:** Parsed date columns, extracted integers from price (`"$5,500"` → `5500`) and odometer (`"150,000 km"` → `150000`).
- **Irrelevant columns dropped:** Removed scraping metadata, near‑zero variance columns (`num_pictures`), and free‑text fields (`name`, `model`).
- **Missing value handling:** Filled categorical missing values (`vehicle_type`, `gearbox`, `fuel_type`, `unrepaired_damage`) with `"unknown"` to preserve rows for price/brand/age analysis.

### 2. Outlier Removal (Rule‑Based Capping)

We applied documented bounds to simulate standard market conditions:

| Column              | Lower bound | Upper bound | Rationale |
|---------------------|-------------|-------------|-----------|
| `price`             | 500 €       | 250,000 €   | Removes token ads (1–499) and hyper‑exotic listings |
| `registration_year` | 1950        | 2016        | Excludes pre‑1950 antiques and future years |
| `car_age`           | 0           | (no cap)    | Negative ages are data errors |
| `odometer_km`       | 0 km        | 500,000 km  | Unrealistic for a running car |
| `power_ps`          | 1 PS        | 1,000 PS    | Removes 0‑PS errors and hypercar territory |

**Result:** 39,759 high‑quality records retained (20.5% of original noise removed).

---

## 📈 Market Insights (EDA)

### 1. The Primary Drivers of Depreciation

- **Price vs. Age:** Steepest drop in first 5 years (new‑car premium evaporates), then a long flat tail. Spike beyond ~25 years is survivor bias (collector market).
- **Price vs. Mileage:** Pearson correlation of **−0.433**; mileage alone explains ≈17% of price variance (R² = 0.187). Brand and age account for the remaining ~81%.
- **Price vs. Brand:** Porsche (€33,900 median), Land Rover (€12,700), Mini (€9,100) lead the market. Premium brands command 3–5× higher prices than volume brands (Opel, Fiat, Renault).

### 2. Brand Value Retention Leaderboard

We evaluated retention using a **fixed reference age comparison** (price at age 10 / price at age 3) and a **log‑linear regression** (log(price) ~ age) to extract annual depreciation rates.

**Top 5 brands by value retention (age 10 vs. age 3):**

| Brand     | Retention Ratio |
|-----------|-----------------|
| Hyundai   | 54.6%           |
| Suzuki    | 50.0%           |
| Seat      | 39.8%           |
| Renault   | 38.4%           |
| Smart     | 37.5%           |

**Annual depreciation rate (log‑linear regression, R² ≥ 0.30):**

- **Green tier (<5%/yr):** Daihatsu (4.57%) – excellent for extended inventory holding.
- **Yellow tier (5‑10%/yr):** Honda (6.42%), Suzuki (6.96%), Mazda (8.05%).
- **Red tier (>10%/yr):** Subaru (12.47%), Kia (16.38%) – require fast turnover.

### 3. Mileage Sensitivity by Vehicle Type

Utility vehicles (SUVs) retain significant value even past 100,000 km, while sports cars (coupes, convertibles) lose over half their value once heavily driven. Dealers should stock high‑mileage SUVs over high‑mileage coupes/sedans.

---

## 💡 Actionable Business Recommendations

Translating data into strategy, this analysis yields three direct recommendations:

1. **Inventory Sourcing Strategy** – Aggressively source **high‑mileage SUVs** over high‑mileage coupes/sedans, as SUVs maintain robust profit margins late into their lifecycle.
2. **Purchasing Optimization** – Consumers and corporate fleets seeking luxury vehicles (BMW/Audi) should buy on the secondary market **after year 4** to bypass the steepest depreciation cliff.
3. **Appraisal Automation** – Dealerships can use the deployed pricing estimator to instantly standardise trade‑in offers, reducing appraisal time and eliminating human bias.

---

## 🤖 Pricing Intelligence Tool

Instead of a black‑box machine learning model, we built a **deterministic lookup‑based estimator** – fully interpretable and grounded in real market medians and percentiles (Q1 – median – Q3).

### How it works

1. **Exact match** – brand + car_age + mileage bin → return Q1, median, Q3, and sample count.
2. **Nearest age** – same brand and mileage bin, pick the row with closest age.
3. **Brand‑only median** – ignore mileage and age, return brand‑level quartiles.
4. **Overall market** – brand unknown → global quartiles.

The tool automatically warns when the sample size is small (<5 records) or when a fallback level is used.

### Example predictions

| Brand          | Mileage | Age | Q1 (€) | Median (€) | Q3 (€) | Fallback level |
|----------------|---------|-----|--------|------------|--------|----------------|
| Porsche        | 85,000  | 6   | 36,125 | **38,950** | 54,625 | 1 (exact)      |
| Mercedes‑Benz  | 30,000  | 3   | 21,940 | **29,900** | 35,700 | 1 (exact)      |
| Volkswagen     | 120,000 | 10  | 4,512  | **5,999**  | 7,612  | 1 (exact)      |
| Ford           | 200,000 | 15  | 1,150  | **2,499**  | 5,400  | 3 (brand‑only) |

---

## 🚀 Deployment & Usage

### 1. Real‑Time Pricing Estimator (Streamlit Dashboard)

We transformed the static Python logic into an interactive web application using **Streamlit**. Stakeholders can enter any brand, age, and mileage and instantly receive a market‑validated price range alongside brand depreciation insights and the price vs. age curve.

**Live demo:** [https://ebay-auto-pricing-estimator-demo.streamlit.app/](https://ebay-auto-pricing-estimator-demo.streamlit.app/)  
*(Replace with your actual deployed URL)*

### 2. Run the App Locally

```bash
# Clone the repository
git clone https://github.com/NexTech-Solution/Ebay_Market_Intelligence.git
cd Ebay_Market_Intelligence

# (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Launch the Streamlit app
streamlit run app.py

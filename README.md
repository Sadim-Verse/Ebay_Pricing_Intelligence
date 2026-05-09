# 🚗 eBay Kleinanzeigen – Used Car Pricing Intelligence

**Python · Pandas · Streamlit · Matplotlib · Seaborn**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app/)  
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Project Overview

The secondary car market on eBay Kleinanzeigen is full of messy, user‑generated data – placeholders, missing fields, and unrealistic prices.  
This project transforms that raw data into **clean, actionable market intelligence**.

**What we deliver:**

- A documented **data cleaning pipeline** that removes >10,000 invalid entries.
- **Exploratory analysis** revealing the real drivers of depreciation: brand, age, mileage.
- **Value retention rankings** (brands that hold value best, annual depreciation rates).
- A **deterministic pricing estimator** that returns Q1, median, Q3 prices based on brand, age, and mileage.
- An interactive **Streamlit dashboard** for real‑time pricing and depreciation insights.

> **No black‑box models** – the pricing logic is fully interpretable (lookup + fallback).

---

## 🛠️ Data Engineering & Cleaning

Raw input: 50,000 listings, 20 columns.  
After cleaning: **39,759 high‑quality rows** (20.5% noise removed).

### Key cleaning steps

| Step                     | Action                                                                 |
|--------------------------|------------------------------------------------------------------------|
| **Column renaming**      | German → English, snake_case (`yearOfRegistration` → `registration_year`) |
| **Type casting**         | Prices, odometer → integers; dates → datetime                           |
| **Drop irrelevant**      | `num_pictures`, scraping metadata, `name`, `model`, `offer_type`       |
| **Handle missing**       | Categorical fields → `"unknown"` (preserve rows)                       |
| **Outlier capping**      | Price 500–250k, year 1950–2016, odometer 0–500k, power 1–1000 PS       |

**Result:** Price skewness drops from 184.91 → 5.73. The distribution becomes realistic and benchmark‑ready.

---

## 📊 Exploratory Analysis – Market Drivers

### 1. Price vs. Age

- **Steepest drop** occurs in the first 5 years (new‑car premium disappears).
- **Flat tail** from age 6 to ≈20 years.
- **Spike after 25 years** – survivor bias (collector cars, not normal inventory).

### 2. Price vs. Mileage

- Pearson correlation: **−0.433** (moderate, not dominant).
- R² = 0.187 → mileage alone explains **~19%** of price variance.  
  → Brand and age explain the remaining 81%.

### 3. Price vs. Brand (median price, ≥50 listings)

| Brand        | Median Price (€) |
|--------------|------------------|
| Porsche      | 33,900           |
| Land Rover   | 12,700           |
| Mini         | 9,100            |
| Jeep         | 8,600            |
| sonstige     | 8,500            |

Premium brands command 3–5× higher prices than volume brands – higher margin but slower turnover.

---

## 📉 Value Retention Analysis

We use two complementary methods to rank brands by how well they hold value.

### A. Fixed Reference Age Ratio

Compare median price at **age 10** vs. **age 3**.

| Brand     | Retention Ratio |
|-----------|-----------------|
| Hyundai   | 54.6%           |
| Suzuki    | 50.0%           |
| Seat      | 39.8%           |
| Renault   | 38.4%           |
| Smart     | 37.5%           |

### B. Annual Depreciation Rate (Log‑Linear Regression)

`log(price) ~ age` → slope = annual % loss (filtered: ≥10 age points, R² ≥ 0.30).

- **Green (<5%/yr):** Daihatsu (4.57%) – safest for extended inventory.
- **Yellow (5–10%/yr):** Honda (6.42%), Suzuki (6.96%), Mazda (8.05%).
- **Red (>10%/yr):** Subaru (12.47%), Kia (16.38%) – must be turned over quickly.

> Full tables are available in the notebook and Streamlit dashboard.

---

## 🤖 Pricing Intelligence Tool

**Deterministic, look‑up based** – no randomness, fully transparent.

### Fallback logic (4 levels)

1. **Exact match** – brand + exact age + mileage bin → return Q1, median, Q3, sample count.
2. **Nearest age** – same brand + mileage bin, pick the row with closest age.
3. **Brand‑only median** – ignore mileage and age.
4. **Overall market** – brand unknown → global quartiles.

The tool warns when sample size is small (<5 records) or when a fallback is used.

### Example outputs

| Brand          | Mileage | Age | Q1 (€) | Median (€) | Q3 (€) | Fallback |
|----------------|---------|-----|--------|------------|--------|----------|
| Porsche        | 85,000  | 6   | 36,125 | **38,950** | 54,625 | 1 (exact) |
| Mercedes‑Benz  | 30,000  | 3   | 21,940 | **29,900** | 35,700 | 1 (exact) |
| Volkswagen     | 120,000 | 10  | 4,512  | **5,999**  | 7,612  | 1 (exact) |
| Ford           | 200,000 | 15  | 1,150  | **2,499**  | 5,400  | 3 (brand)  |

---

## 🚀 Deployment – Streamlit Dashboard

We packaged the pricing logic and key charts into an interactive web app.

**Live demo:** [https://your-app-url.streamlit.app/](https://your-app-url.streamlit.app/)  
*(Replace with your actual deployed URL)*

### Dashboard features

- **Pricing estimator** – enter brand, age, mileage → instant Q1/median/Q3 + confidence notes.
- **Depreciation rates** – table + coloured bar chart (green <5%, yellow 5‑10%, red >10%).
- **Price vs. age curve** – visual depiction of the whole‑market depreciation pattern.

### Run locally

```bash
git clone https://github.com/NexTech-Solution/Ebay_Market_Intelligence.git
cd Ebay_Market_Intelligence
pip install -r requirements.txt
streamlit run app.py

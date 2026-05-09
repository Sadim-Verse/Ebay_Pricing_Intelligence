# Ebay_Market_Intelligence

# 🚗 eBay Kleinanzeigen – Used Car Market Intelligence & Pricing Tool

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project transforms raw, noisy eBay Kleinanzeigen used car data into **actionable pricing intelligence**.  
It includes:

- A **complete data cleaning & EDA pipeline** (Jupyter Notebook).
- A **deterministic pricing estimator** (median + quartiles based on brand, age, and mileage).
- A **Streamlit dashboard** for interactive pricing and depreciation insights.

> **Real‑world impact:** The final pricing tool helps dealers, resellers, and marketplace platforms avoid overpriced inventory, identify undervalued deals, and automatically flag suspicious listings.

---

## 📊 Key Insights from the Analysis

| Finding | Business Implication |
|---------|----------------------|
| Premium brands (Porsche, Land Rover) command 3–5× higher median prices | Higher per‑unit margin, but slower turnover; balance inventory accordingly. |
| Steepest price drop occurs in first 5 years (new‑car premium evaporates) | Buy at 3–5 years old, sell before year 9 to capture the flat part of the curve. |
| Mileage alone explains ≈17% of price variance | Never price on mileage alone – brand and age are equally important. |
| Brands with <5% annual depreciation retain value best | Safe long‑hold assets; brands with >10% depreciation must be turned over quickly. |
| Cars older than 25 years spike in price (survivor bias / collector market) | Treat vintage cars as a separate segment (specialist valuation required). |

---

## 📁 Repository Structure

# 🍷 Wine Quality Control Dashboard

A data science approach to quality control — applying Statistical Process 
Control (SPC) and Process Capability (Cpk) analysis to 6,497 wine samples.

## Project Overview
This dashboard audits physicochemical parameters across red and white wine 
production using OIV and EU Regulation 606/2009 standards — asking the 
question a QC chemist asks: is this process in control, and what does a 
failing batch look like chemically?

## Dashboard Pages
- 📊 Executive Summary — KPI cards, pass/fail analysis, parameter health
- 🔬 Parameter Profiles — distributions, box plots, correlation heatmap
- 📈 SPC Analysis — control charts, Cpk capability, OOS frequency
- 🎯 Quality Drivers — correlation analysis, root cause table
- ⚗️ Red vs White — chemical profile comparison

## Tools & Libraries
- Python, Pandas, NumPy
- Plotly, Matplotlib, Seaborn
- Streamlit

## Dataset
Cortez et al. (2009). Wine Quality. UCI Machine Learning Repository.
https://archive.ics.uci.edu/dataset/186/wine+quality

## Standards Applied
- OIV Annex C — Maximum Acceptable Limits
- EU Regulation 606/2009 — Oenological Practices
- EU Regulation 1308/2013 — Wine Categories
- Food industry Cpk threshold ≥ 1.0 applied

## Author
Edith Sunday - QC Chemist | Data Analyst
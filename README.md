# wti-cftc-flow-analysis-Ols-regression
Flow-based econometric analysis of NYMEX WTI crude oil prices using CFTC positioning data and robust OLS regression.
# What Drives NYMEX WTI Oil Prices?
## Evidence from CFTC Positioning Flows and Robust OLS Regression

This project studies whether short-term NYMEX WTI crude oil price movements are better explained by **financial positioning flows** than by a standard **macro-factor model**.

Using weekly CFTC Disaggregated Commitments of Traders data merged with WTI futures prices from Yahoo Finance, I estimate a robust OLS model on changes in trader net positions across four market participant categories.

## Research Question

Do futures market positioning flows from Managed Money, Swap Dealers, Producers, and Other Reportables explain weekly WTI price changes?

## Data

- **CFTC Disaggregated COT**: weekly trader positioning on `WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE`
- **Yahoo Finance (`CL=F`)**: WTI futures prices
- **Macro benchmark variables**: DXY, S&P 500, VIX, US 10Y yield
- Sample: **144 weekly observations (2023–2025)**

## Methodology

1. Extract weekly net positions by trader group  
2. Merge CFTC positioning with WTI futures prices  
3. Compute weekly first differences  
4. Estimate OLS regressions with **HC1 robust standard errors**  
5. Run residual diagnostics and compare against a macro benchmark model

## Main Findings

- Flow-based model **R² = 0.539**
- Macro benchmark model **R² = 0.143**
- All four CFTC trader groups are statistically significant
- Managed Money shows the strongest marginal relationship with weekly WTI price changes
- Residual diagnostics indicate **fat tails**, **non-normality**, and support robust inference

## Interpretation

The results support the **financialization thesis**: short-term WTI price action appears to be driven more by **paper-barrel positioning flows** than by standard macro factors over the sample period.

This has direct relevance for:
- commodity research,
- producer/refiner hedging,
- airline and shipping fuel procurement,
- short-term trading signal generation.

## Key Visuals

- Physical vs Financial Volume
- Scatter Plot: WTI Price Changes vs Managed Money Flows
- Rolling 52-Week Beta
- Q-Q Plot of Residuals
- Residual Distribution
- Residuals vs Fitted

## Repository Structure

- `data/` – raw and processed datasets  
- `notebooks/` – exploratory and presentation notebook  
- `src/` – data preparation and econometric scripts  
- `outputs/` – figures and regression tables  
- `docs/` – presentation and short report  

## How to Run

```bash
pip install -r requirements.txt
python src/data_prep.py
python src/regression_model.py
python src/diagnostics.py

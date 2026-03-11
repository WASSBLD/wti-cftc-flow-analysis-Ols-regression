# Financial Flows and Price Formation in the NYMEX WTI Market
## Quantitative Evidence from CFTC Positioning Data

Below is a structured analytical description consistent with how a commodities strategist or quantitative analyst at a large sell-side institution would present the results. The interpretation is strictly based on the material contained in the uploaded documents and regression outputs.

---

## 1. Research Team and Core Objective

The research project was conducted by a quantitative research group focusing on market microstructure in commodity futures markets, with the central objective of identifying alpha-relevant signals embedded in trader positioning data.

The empirical objective is to determine whether changes in futures positions held by major trader categories explain short-term price movements in the NYMEX WTI crude oil market. The analysis uses Ordinary Least Squares (OLS) regression to quantify the relationship between weekly changes in trader net positions and weekly changes in WTI futures prices.

The regression framework estimates:

\[
\Delta Oil_t = \alpha + \beta_1 \Delta HF_t + \beta_2 \Delta Swap_t + \beta_3 \Delta Prod_t + \beta_4 \Delta Other_t + \epsilon_t
\]

Where:

- \(\Delta Oil_t\) = weekly change in WTI futures price (USD/barrel)
- \(\Delta HF_t\) = change in Managed Money net positions
- \(\Delta Swap_t\) = change in Swap Dealer net positions
- \(\Delta Prod_t\) = change in Producer/Merchant net positions
- \(\Delta Other_t\) = change in Other Reportables net positions

The goal is therefore to test whether positioning flows from different trader groups generate statistically significant predictive signals for price movements, i.e., whether financial positioning constitutes a measurable driver of oil price volatility.

The sample covers 144 weekly observations from 2023–2025, derived from the CFTC Disaggregated Commitments of Traders dataset combined with WTI futures prices.

---

## 2. The Financialization Thesis

A key conceptual foundation of the analysis is the financialization of the oil market.

Modern crude oil markets exhibit a large divergence between physical market flows and financial trading activity.

Empirical estimates indicate:

| Market Flow | Daily Volume |
|---|---:|
| Physical crude consumption | ~100 million barrels/day |
| Futures trading volume | ~6 billion barrels/day |

This implies approximately:

**60:1 ratio of financial barrels to physical barrels**

In other words, for every barrel physically consumed, roughly 60 barrels are traded in derivative markets.

This structural imbalance implies that futures markets increasingly determine price discovery, as financial participants trade exposures far exceeding underlying physical flows.

As a consequence:

- Position changes by financial actors can generate significant short-term price pressure
- Physical supply-demand fundamentals influence prices more gradually
- Futures markets act as the primary transmission mechanism for price volatility

The empirical regression tests this hypothesis directly by quantifying how financial positioning translates into price movements.

---

## 3. Market Participants and Economic Roles

The CFTC Disaggregated Commitments of Traders report separates market participants into four economically distinct groups.

### Managed Money (Speculators)

Managed Money represents:

- Hedge funds
- Commodity Trading Advisors (CTAs)
- Quantitative funds

These actors are purely speculative participants whose objective is to extract returns from price movements.

Characteristics:

- Highly reactive to macro signals and momentum
- Frequently operate systematic strategies
- Tend to amplify price trends

Their net positions often serve as a proxy for speculative sentiment in the oil market.

### Producers / Merchants / Processors / Users

This group represents commercial hedgers.

Examples:

- Oil producers
- Refiners
- Integrated energy companies

These participants typically short futures contracts to hedge future production, reducing exposure to price volatility.

Their positioning reflects hedging pressure rather than directional speculation.

### Swap Dealers

Swap dealers are primarily:

- Investment banks
- Commodity desks
- Structured product providers

They act as intermediaries between financial investors and physical market participants.

For example:

- An institutional investor wanting oil exposure may enter a swap with a bank.
- The bank hedges this exposure by trading futures.

Thus swap dealers transmit financial flows into futures markets.

### Other Reportables

This category includes:

- Commodity trading houses
- Large institutional investors
- Proprietary trading firms

Their activity often overlaps with speculative positioning and may reflect large discretionary macro trades.

Together, these groups represent the dominant sources of open interest in the WTI futures market, making them critical determinants of price dynamics.

---

## 4. Data Integration and Python Pipeline

The empirical analysis required merging two independent datasets.

### CFTC Positioning Data

**Source:**  
CFTC Disaggregated Commitments of Traders (COT) report

Variables extracted:

- Managed Money net positions
- Producer/Merchant net positions
- Swap Dealer net positions
- Other Reportables net positions

Net positions were computed as:

\[
Net = Long\ Positions - Short\ Positions
\]

### WTI Price Data

**Source:**  
Yahoo Finance (ticker: `CL=F`)

Daily WTI futures prices were downloaded using the Python `yfinance` API, then resampled to weekly frequency.

Additional macro factors were also downloaded:

- DXY (US Dollar Index)
- S&P 500
- VIX
- US 10Y Treasury yield

### Data Processing Pipeline

The workflow implemented in Python included:

- Download daily futures prices
- Convert daily prices to weekly frequency
- Merge price data with CFTC weekly reports
- Compute first differences for stationarity

\[
\Delta X_t = X_t - X_{t-1}
\]

- Estimate OLS regression with heteroskedasticity-robust standard errors (HC1)

---

## 5. Description of Diagnostic Plots

The research includes a set of market-microstructure visualizations designed to analyze the relationship between financial flows and price dynamics.

### Plot 1 — Physical vs Financial Volume

This chart illustrates the scale difference between physical oil demand and financial derivatives trading.

The visual highlights:

- Physical demand ~100 million barrels/day
- Financial futures turnover ~6 billion barrels/day

This confirms the structural dominance of financial markets in price discovery.

### Plot 2 — Scatter Plot: Price Change vs Hedge Fund Flows

This plot shows:

- **x-axis:** weekly change in hedge fund net positions
- **y-axis:** weekly change in WTI prices

The distribution reveals a clear positive relationship:

- Net buying by hedge funds is associated with price increases
- Net selling corresponds with price declines

This pattern suggests that speculative flows act as a short-term price driver.

### Plot 3 — Rolling 52-Week Beta

The rolling beta estimates the time-varying sensitivity of WTI prices to hedge fund positioning.

Observed characteristics:

- Beta is positive during most periods
- Sensitivity increases during periods of elevated volatility
- Relationship strengthens during directional markets

This indicates that financial flows exert stronger influence during trending regimes.

### Plot 4 — Q-Q Plot of Residuals

The quantile-quantile plot compares regression residuals with a normal distribution.

Findings:

- Residuals deviate strongly in the tails
- Extreme observations exceed theoretical normal quantiles

This indicates fat-tailed error distribution, typical in financial return series.

### Plot 5 — Residuals Distribution

The histogram of residuals shows:

- Heavy tails
- Slight negative skew

This confirms that WTI returns exhibit non-Gaussian behavior, a standard feature in commodity markets.

### Plot 6 — Residuals vs Fitted Values

This diagnostic plot examines heteroscedasticity.

The pattern reveals:

- Increasing variance of residuals at higher fitted values
- Evidence of volatility clustering

This implies that OLS residual variance is not constant, requiring robust standard errors.

---

## 6. Interpretation of the Visual Evidence

The graphical diagnostics support several structural conclusions about the WTI futures market.

### Futures Market Volatility

Oil price changes display heteroskedastic behavior, with volatility clustering during periods of strong financial flows.

### Position Imbalances

Large shifts in speculative positioning generate temporary demand imbalances in the futures order book, contributing to price swings.

### Hedging Pressure

Producer hedging activity introduces structural short pressure, while speculative flows periodically offset this imbalance.

The interaction between these forces drives short-term price movements.

---

## 7. OLS Regression Results

The regression results are summarized below.

| Variable | Coefficient | Significance |
|---|---:|---|
| Managed Money | ~0.0002 | *** highly significant |
| Swap Dealers | ~0.0001 | significant |
| Producers | ~0.0001 | significant |
| Other Reportables | ~0.0002 | *** highly significant |

### Model Statistics

- **R² = 0.539**
- **Adjusted R² = 0.525**
- **F-statistic = 63.57**
- **p-value ≈ 1.9 × 10⁻³⁰**

### Interpretation

Approximately 54% of the weekly variance in WTI price changes is explained by futures positioning flows.

For a commodity return regression, this is exceptionally high explanatory power.

---

## 8. Diagnostic Analysis and Econometric Corrections

Residual diagnostics revealed several statistical issues.

### Non-Normality

Jarque-Bera test strongly rejects normality.

The residual distribution exhibits:

- Skewness ≈ −0.72
- Kurtosis ≈ 9.27

This indicates fat tails, consistent with commodity return distributions.

### Heteroscedasticity

Residual-variance plots show non-constant variance.

To correct this issue, the regression uses:

**HC1 robust standard errors**

This adjustment produces consistent t-statistics even in the presence of heteroscedasticity, ensuring valid inference.

---

## 9. Strategic Implications for Industry Participants

The findings have direct implications for energy market participants.

### Energy Producers

Producers can optimize hedging strategies by monitoring speculative positioning.

Large speculative inflows may indicate temporary price rallies, creating favorable hedging opportunities.

### Refiners

Refiners can adjust crude procurement strategies based on position-driven price momentum.

Monitoring Managed Money flows may improve short-term price timing.

### Airlines and Shipping Companies

Fuel-intensive industries can improve fuel cost forecasting by incorporating CFTC positioning indicators into procurement models.

### Trading Desks

Commodity trading desks can treat changes in hedge fund positioning as alpha signals, particularly in short-term systematic strategies.

---

## 10. Final Conclusion

The empirical results strongly support the financialization hypothesis.

### Key Conclusions

- Futures positioning flows explain over half of weekly WTI price variation
- Speculative and financial participants exert significant influence on short-term price formation
- Diagnostic tests confirm non-Gaussian volatility patterns typical of financial markets

### Most Important Takeaway

Short-term WTI price movements are primarily driven by financial positioning rather than physical oil fundamentals.

In practical terms:

The NYMEX crude oil market is dominated by “paper barrels”, and the dynamics of financial flows within the futures market have become the principal determinant of price action.

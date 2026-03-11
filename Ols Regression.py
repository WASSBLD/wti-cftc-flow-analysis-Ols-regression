import os
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

plt.style.use("seaborn-v0_8-darkgrid")

# ------------------------------------------------------------
# 1. I set the paths and key parameters
# ------------------------------------------------------------
FILE_PATH = r"C:\Users\user\PycharmProjects\PythonProject4\Disaggregated_-_Combined_20251124 (2).csv"
MARKET_NAME = "WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE"
START_DATE = "2023-01-01"
ROLLING_WINDOW = 52
ALPHA = 0.05

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(PROJECT_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# ------------------------------------------------------------
# 2. I load the file
# ------------------------------------------------------------
if FILE_PATH.lower().endswith(".csv"):
    df = pd.read_csv(FILE_PATH, low_memory=False)
else:
    df = pd.read_excel(FILE_PATH, sheet_name="Data")

df["date"] = pd.to_datetime(df["Report_Date_as_YYYY_MM_DD"], errors="coerce")
df = df.dropna(subset=["date"])

wti = df[df["Market_and_Exchange_Names"] == MARKET_NAME].copy()
wti = wti[wti["date"] >= START_DATE].copy()
wti = wti.sort_values("date")

if "Swap_Positions_Short_All" in wti.columns:
    swap_short_col = "Swap_Positions_Short_All"
elif "Swap__Positions_Short_All" in wti.columns:
    swap_short_col = "Swap__Positions_Short_All"
else:
    raise ValueError("Swap short column not found.")

# ------------------------------------------------------------
# 3. I convert the position columns to numeric and build weekly net positions
# ------------------------------------------------------------
numeric_cols = [
    "M_Money_Positions_Long_All",
    "M_Money_Positions_Short_All",
    "Prod_Merc_Positions_Long_All",
    "Prod_Merc_Positions_Short_All",
    "Swap_Positions_Long_All",
    swap_short_col,
    "Other_Rept_Positions_Long_All",
    "Other_Rept_Positions_Short_All",
]

for col in numeric_cols:
    wti[col] = pd.to_numeric(
        wti[col].astype(str).str.replace(",", "", regex=False).str.strip(),
        errors="coerce"
    )

wti = wti.dropna(subset=numeric_cols)

wti["hf_net"] = wti["M_Money_Positions_Long_All"] - wti["M_Money_Positions_Short_All"]
wti["prod_net"] = wti["Prod_Merc_Positions_Long_All"] - wti["Prod_Merc_Positions_Short_All"]
wti["swap_net"] = wti["Swap_Positions_Long_All"] - wti[swap_short_col]
wti["other_net"] = wti["Other_Rept_Positions_Long_All"] - wti["Other_Rept_Positions_Short_All"]

wti = wti[["date", "hf_net", "prod_net", "swap_net", "other_net"]]
wti = wti.sort_values("date").reset_index(drop=True)

print("CFTC rows:", len(wti))
print(wti.head())

# ------------------------------------------------------------
# 4. I download WTI futures prices from Yahoo Finance
# ------------------------------------------------------------
end_date = (wti["date"].max() + pd.Timedelta(days=7)).strftime("%Y-%m-%d")

oil_raw = yf.download(
    "CL=F",
    start=START_DATE,
    end=end_date,
    interval="1d",
    progress=False,
    auto_adjust=False
).reset_index()

if isinstance(oil_raw.columns, pd.MultiIndex):
    oil_raw.columns = ["_".join([str(c) for c in col if c != ""]) for col in oil_raw.columns]

date_col = [c for c in oil_raw.columns if "date" in c.lower()][0]

price_col = None
for c in oil_raw.columns:
    if "adj" in c.lower() and "close" in c.lower():
        price_col = c
        break

if price_col is None:
    close_candidates = [c for c in oil_raw.columns if "close" in c.lower()]
    price_col = close_candidates[0]

oil = oil_raw[[date_col, price_col]].rename(columns={date_col: "date", price_col: "oil_price"})
oil["date"] = pd.to_datetime(oil["date"])
oil = oil.sort_values("date").reset_index(drop=True)

print("Oil rows:", len(oil))
print(oil.head())

# ------------------------------------------------------------
# 5. I merge weekly CFTC data with the closest available oil price
# ------------------------------------------------------------
merged = pd.merge_asof(
    wti.sort_values("date"),
    oil.sort_values("date"),
    on="date",
    direction="backward"
).dropna(subset=["oil_price"])

print("\nMerged rows:", len(merged))
print(merged.head())

# ------------------------------------------------------------
# 6. I compute first differences
# ------------------------------------------------------------
merged["d_oil"] = merged["oil_price"].diff()
merged["d_hf"] = merged["hf_net"].diff()
merged["d_prod"] = merged["prod_net"].diff()
merged["d_swap"] = merged["swap_net"].diff()
merged["d_other"] = merged["other_net"].diff()

reg_data = merged.dropna(subset=["d_oil", "d_hf", "d_swap", "d_prod", "d_other"]).copy()
reg_data = reg_data.sort_values("date").reset_index(drop=True)

# ------------------------------------------------------------
# 7. I estimate the multi-factor OLS with HC1 robust errors
# ------------------------------------------------------------
Y = reg_data["d_oil"]
X = sm.add_constant(reg_data[["d_hf", "d_swap", "d_prod", "d_other"]])

model = sm.OLS(Y, X).fit(cov_type="HC1")

print("\n================ MULTI-FACTOR REGRESSION (HC1) ================")
print(model.summary())

coef_table = pd.DataFrame({
    "variable": model.params.index,
    "coef": model.params.values,
    "robust_std_err": model.bse.values,
    "t_stat": model.tvalues.values,
    "p_value": model.pvalues.values
})

print("\n================ COEFFICIENTS TABLE ================")
print(coef_table.to_string(index=False))

jb_stat, jb_pvalue, skewness, kurtosis = sm.stats.stattools.jarque_bera(model.resid)

diagnostics_table = pd.DataFrame({
    "metric": [
        "Observations",
        "R-squared",
        "Adjusted R-squared",
        "F-statistic",
        "F p-value",
        "Jarque-Bera",
        "JB p-value",
        "Skewness",
        "Kurtosis"
    ],
    "value": [
        int(model.nobs),
        model.rsquared,
        model.rsquared_adj,
        model.fvalue,
        model.f_pvalue,
        jb_stat,
        jb_pvalue,
        skewness,
        kurtosis
    ]
})

print("\n================ MODEL DIAGNOSTICS ================")
print(diagnostics_table.to_string(index=False))

# ------------------------------------------------------------
# 8. I prepare fitted values and residuals
# ------------------------------------------------------------
reg_data["fitted"] = model.fittedvalues
reg_data["residual"] = model.resid

# ------------------------------------------------------------
# 9. I compute all pieces needed for the 6 plots
# ------------------------------------------------------------
simple_model = sm.OLS(reg_data["d_oil"], sm.add_constant(reg_data["d_hf"])).fit()
x_line = np.linspace(reg_data["d_hf"].min(), reg_data["d_hf"].max(), 200)
x_line_df = pd.DataFrame({"const": 1.0, "d_hf": x_line})
y_line = simple_model.predict(x_line_df)

cov_rolling = reg_data["d_oil"].rolling(ROLLING_WINDOW).cov(reg_data["d_hf"])
var_rolling = reg_data["d_hf"].rolling(ROLLING_WINDOW).var()
rolling_beta = cov_rolling / var_rolling

qq = stats.probplot(reg_data["residual"], dist="norm")
theoretical_quantiles = qq[0][0]
sample_quantiles = qq[0][1]
slope, intercept = qq[1][0], qq[1][1]

resid = reg_data["residual"]
mu = resid.mean()
sigma = resid.std(ddof=1)
x_norm = np.linspace(resid.min() - 1, resid.max() + 1, 500)
normal_density = stats.norm.pdf(x_norm, loc=mu, scale=sigma)

df_resid = int(model.df_resid)
t_crit = stats.t.ppf(1 - ALPHA / 2, df_resid)
t_values = model.tvalues[["d_hf", "d_swap", "d_prod", "d_other"]]

x_t_min = min(-4.5, t_values.min() - 0.7)
x_t_max = max(4.5, t_values.max() + 0.7)
x_t = np.linspace(x_t_min, x_t_max, 1200)
y_t = stats.t.pdf(x_t, df=df_resid)

# ------------------------------------------------------------
# 10. I show all 6 plots in one screen and save the dashboard
# ------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(22, 12))
fig.suptitle("WTI Flow-Based OLS Regression Diagnostics and Market Plots", fontsize=16, y=1.02)

ax = axes[0, 0]
ax.scatter(reg_data["d_hf"], reg_data["d_oil"], alpha=0.6, label="Weekly data")
ax.plot(x_line, y_line, color="red", linewidth=2, label="OLS fit (ΔOil ~ ΔHF)")
ax.set_xlabel("Δ Managed Money Net (contracts)")
ax.set_ylabel("Δ WTI Price (USD)")
ax.set_title("ΔOil vs ΔHF (with fitted regression line)")
ax.legend()

ax = axes[0, 1]
ax.plot(reg_data["date"], rolling_beta, linewidth=2)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title(f"Rolling {ROLLING_WINDOW}-week β: ΔWTI ~ ΔHF")
ax.set_xlabel("Date")
ax.set_ylabel("Rolling Beta")

ax = axes[0, 2]
ax.scatter(reg_data["fitted"], reg_data["residual"], alpha=0.7)
ax.axhline(0, color="red", linewidth=1.5)
ax.set_xlabel("Fitted ΔOil")
ax.set_ylabel("Residual")
ax.set_title("Residuals vs Fitted Values")

ax = axes[1, 0]
ax.scatter(theoretical_quantiles, sample_quantiles)
ax.plot(
    theoretical_quantiles,
    slope * theoretical_quantiles + intercept,
    color="red",
    linewidth=2
)
ax.set_xlabel("Theoretical Quantiles")
ax.set_ylabel("Sample Quantiles")
ax.set_title("Q-Q Plot of Residuals (vs Normal)")

ax = axes[1, 1]
ax.hist(resid, bins=18, density=True, alpha=0.55, label="Residuals histogram")
ax.plot(x_norm, normal_density, linewidth=2, label="Normal(μ,σ²) fit")
ax.set_xlabel("Residual")
ax.set_ylabel("Density")
ax.set_title("Residuals: Histogram & Normal Density")
ax.legend()

ax = axes[1, 2]
ax.plot(x_t, y_t, linewidth=2, label=f"t-dist(df={df_resid})")

left_tail = x_t[x_t <= -t_crit]
right_tail = x_t[x_t >= t_crit]
ax.fill_between(left_tail, stats.t.pdf(left_tail, df=df_resid), alpha=0.35, label="Rejection region (α/2 each)")
ax.fill_between(right_tail, stats.t.pdf(right_tail, df=df_resid), alpha=0.35)

ax.axvline(-t_crit, color="red", linestyle=":", linewidth=2)
ax.axvline(t_crit, color="red", linestyle=":", linewidth=2)

line_specs = [
    ("d_hf", "blue"),
    ("d_swap", "green"),
    ("d_prod", "orange"),
    ("d_other", "purple"),
]

for var, color in line_specs:
    t_val = model.tvalues[var]
    ax.axvline(t_val, color=color, linestyle="--", linewidth=2, label=f"t({var}) = {t_val:.2f}")

ax.set_xlim(x_t_min, x_t_max)
ax.set_xlabel("t value")
ax.set_ylabel("Density")
ax.set_title(f"t-distribution with rejection regions (α = {ALPHA:.2f})")
ax.legend(fontsize=9)

plt.tight_layout()

plot_file = os.path.join(PLOTS_DIR, "wti_ols_6plots_dashboard.png")
plt.savefig(plot_file, dpi=300, bbox_inches="tight")

plt.show()

print(f"\nPlot saved in: {plot_file}")
print(f"Plots folder: {PLOTS_DIR}")
print("Files in plots folder:", os.listdir(PLOTS_DIR))
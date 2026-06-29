import yfinance as yf
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
import matplotlib.pyplot as plt
from dateutil.parser import parse
from datetime import datetime
from scipy.stats import norm

# pull options data
ticker = yf.Ticker("SPY")
spot = ticker.history(period="1d")["Close"].iloc[-1]
print(f"SPY spot price: {spot:.2f}")

today = datetime.now()

expiries = ['2026-07-17', '2026-08-21', '2026-09-18', '2026-12-18', '2027-03-19']

all_data = []

for exp in expiries:
    chain = ticker.option_chain(exp)
    calls = chain.calls.copy()
    calls['expiry'] = exp
    days = (parse(exp) - today).days
    calls['T'] = days / 365
    calls['mid'] = (calls['bid'] + calls['ask']) / 2
    calls = calls[(calls['bid'] > 0) & (calls['ask'] > 0)]
    calls = calls[(calls['strike'] > spot * 0.85) & (calls['strike'] < spot * 1.15)]
    all_data.append(calls)
    print(f"{exp}: {len(calls)} contracts loaded")

# black scholes IV extraction
r = 0.045  # risk-free rate (approx 3-month T-bill)
q = 0.013  # SPY dividend yield

def bs_call_price(S, K, T, r, q, sigma):
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def get_iv(market_price, S, K, T, r, q):
    try:
        iv = brentq(lambda sigma: bs_call_price(S, K, T, r, q, sigma) - market_price, 1e-6, 10)
        return iv
    except:
        return np.nan

# apply IV extraction to all contracts
import pandas as pd
df = pd.concat(all_data, ignore_index=True)

print("Extracting implied volatilities...")
df['iv'] = df.apply(lambda row: get_iv(row['mid'], spot, row['strike'], row['T'], r, q), axis=1)
df = df.dropna(subset=['iv'])
df = df[(df['iv'] > 0.01) & (df['iv'] < 2.0)]  # filter out bad IVs

print(f"Successfully extracted IV for {len(df)} contracts")
print(df[['strike', 'expiry', 'T', 'mid', 'iv']].head(10))

from scipy.interpolate import griddata
# plot volatility surface
fig = plt.figure(figsize=(12, 7))
ax = fig.add_subplot(111, projection='3d')

strikes = df['strike'].values
maturities = df['T'].values
ivs = df['iv'].values

# create grid for smooth surface
strike_grid = np.linspace(strikes.min(), strikes.max(), 50)
T_grid = np.linspace(maturities.min(), maturities.max(), 50)
K_mesh, T_mesh = np.meshgrid(strike_grid, T_grid)

# interpolate IV onto grid
iv_mesh = griddata((strikes, maturities), ivs, (K_mesh, T_mesh), method='cubic')

# plot
surf = ax.plot_surface(K_mesh, T_mesh, iv_mesh, cmap='plasma', alpha=0.85)
fig.colorbar(surf, ax=ax, shrink=0.5, label='Implied Volatility')

ax.set_xlabel('Strike')
ax.set_ylabel('Time to Expiry (Years)')
ax.set_zlabel('Implied Volatility')
ax.set_title('SPY Implied Volatility Surface')

plt.tight_layout()
plt.savefig('vol_surface.png', dpi=150)
plt.close()
print("Surface saved as vol_surface.png")
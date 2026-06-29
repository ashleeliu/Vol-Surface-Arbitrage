# Vol-Surface-Arbitrage
In this project, I built a volatility surface analysis tool that extracts implied volatilities from real options data and detects arbitrage violations across strikes and expiries. I ran the analysis on both SPY and VIX options to compare surface behavior across different underlying types.
The tool pulls live options chain data, computes implied volatilities using Black-Scholes, and systematically checks for calendar and butterfly arbitrage conditions across multiple expiration dates.
## What It Does

Loads real options contracts across multiple expiries and extracts implied volatilities using Black-Scholes
Constructs and visualizes a 3D volatility surface across strikes and maturities
Detects calendar arbitrage and butterfly arbitrage violations in the options market
Outputs a structured arbitrage report with violation details by strike and expiry

## Modeling Approach
Implied volatilities are extracted by numerically inverting the Black-Scholes formula for each contract. Arbitrage detection checks:

- Calendar arbitrage: total variance must be non-decreasing across expiries for the same strike
- Butterfly arbitrage: second derivative of price with respect to strike must be non-negative (negative butterfly spread indicates a violation)

## Results
SPY (spot: $740.57, 5 expiries Jul 2026 – Mar 2027):

- 582 contracts analyzed
- 0 calendar arbitrage violations
- 200 butterfly arbitrage violations (largely noise from dense strike spacing and bid-ask spread)
- Arbitrage-free rate: 65.6%

VIX (spot: 17.60, 5 expiries Jul 2026 – Feb 2027):

- 35 contracts analyzed
- 3 calendar arbitrage violations — economically meaningful, driven by VIX options being priced off futures rather than spot VIX, causing total variance to decrease across nearby expiries
- 2 butterfly arbitrage violations
- Arbitrage-free rate: 85.7%
- Near-term implied vols exceed 100%, reflecting the market pricing in vol-of-vol even during a low VIX regime

## Takeaway
SPY's surface is temporally consistent with no calendar violations, while VIX exhibits genuine calendar dislocations explained by its futures-based pricing structure. This highlights how standard no-arbitrage conditions behave differently when the underlying is itself a volatility index.
## Tools

- Python
- Black-Scholes (numerical IV extraction)
- Matplotlib (vol surface visualization)
- yfinance (options data)

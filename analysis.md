# Credit Scoring Analysis

## 1. Score Distribution

The credit scores for wallets are distributed in the range of 0 to 1000, with most scores clustering in the mid to upper range. The distribution is as follows:
-- -- -- -- -- -- -- -- -- -- -- --- -- -- -- --
| Score Range | Number of Wallets | Percentage |
|-------------|------------------|------------|
| 0-100       | 2                | 0.1%       |
| 100-200     | 4                | 0.1%       |
| 200-300     | 92               | 2.6%       |
| 300-400     | 184              | 5.3%       |
| 400-500     | 1313             | 37.5%      |
| 500-600     | 719              | 20.6%      |
| 600-700     | 646              | 18.5%      |
| 700-800     | 476              | 13.6%      |
| 800-900     | 61               | 1.7%       |
| 900-1000    | 0                | 0.0%       |
-- -- -- -- -- -- -- -- -- -- -- --- -- -- -- --

---

## 2. Behavior of Wallets by Score Range

### Low Score Wallets (Score < 300)
- **Typical behaviors:**
  - Very few transactions, often only 1-2.
  - Low or negligible USD volume.
  - High risk indicators (e.g., bot-like activity, only liquidation calls, erratic transaction sizes).
  - Poor or no repayment behavior, or borrowing without deposits.
  - Little to no asset diversification.
- **Interpretation:**  
  These wallets are likely bots, exploit attempts, or users with risky or incomplete engagement with the protocol.

### High Score Wallets (Score ≥ 700)
- **Typical behaviors:**
  - High number of transactions and long activity duration.
  - High total USD volume and consistent transaction sizes.
  - Good diversification across multiple assets.
  - Healthy ratios of deposit, borrow, and repay actions.
  - Low risk indicators, high consistency, and strong repayment behavior.
- **Interpretation:**  
  These wallets represent responsible, active users who interact with the protocol in a healthy, diversified, and consistent manner.

---

## 3. Statistical Summary

- **Mean Score:** 536.59
- **Median Score:** 520.87
- **Standard Deviation:** 135.85
- **Min Score:** 0.00
- **Max Score:** 871.15

---

## 4. Insights

- The majority of wallets fall in the [400-800] range, indicating moderate to good behavior.
- A small percentage of wallets have extremely low scores, often due to inactivity, high risk, or exploitative patterns.
- High scoring wallets tend to have diversified activity, regular usage, and good financial health indicators (repayment, leverage, etc.).
- The scoring model is robust to outliers and penalizes risky or bot-like behavior.

---

## 5. Limitations & Assumptions

- The model is based solely on on-chain transaction data; off-chain creditworthiness is not considered.
- Some wallets may be new or have limited history, which can affect their score.
- The scoring logic is transparent and extensible, but further improvements could include more advanced anomaly detection or time-series analysis.

---

## 6. Score Distribution Graph

![Wallet Credit Score Distribution](score_distribution.png)
 

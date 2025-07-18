# DeFi Credit Scoring System

A robust, explainable machine learning-based credit scoring system for DeFi wallets using Aave V2 transaction data.

---

## Overview

This project analyzes historical transaction behavior on the Aave V2 protocol to assign a **credit score (0-1000)** to each wallet address. Higher scores indicate reliable and responsible usage; lower scores reflect risky, bot-like, or exploitative behavior. The system is transparent, extensible, and designed for both research and production use.

---

## Architecture & Processing Flow

1. **Data Loading**: Parses raw JSON transaction data.
2. **Preprocessing**: Cleans and normalizes transaction amounts, handles token decimals, and computes USD values.
3. **Feature Engineering**: Extracts behavioral, financial, and risk features from transaction history.
4. **Scoring Algorithm**: Calculates a final credit score using a transparent, weighted formula.
5. **Analysis & Visualization**: Generates insights, statistics, and score distribution plots.

---

## Feature Engineering

The following features are engineered for each wallet:

- **Transaction Metrics**
  - `total_transactions`: Number of protocol interactions
  - `unique_assets`: Number of different assets used
  - `total_usd_volume`: Total USD value of all transactions
  - `avg_transaction_size`, `median_transaction_size`

- **Behavioral Patterns**
  - `deposit_ratio`, `borrow_ratio`, `repay_ratio`, `redeem_ratio`, `liquidation_ratio`: Proportion of each action type
  - `activity_duration_days`: Time span of wallet activity
  - `transaction_frequency`: Transactions per day
  - `consistent_usage`: Consistency in transaction timing and amounts

- **Risk & Financial Health**
  - `risk_indicators`: Bot-like or exploitative behavior
  - `leverage_indicator`: Healthy leverage usage
  - `repayment_behavior`: Loan repayment reliability
  - `diversification_score`: Asset portfolio diversification

---

## Scoring Methodology

The credit score is calculated as a weighted sum of feature-based components:

```
final_score = (
    volume_score +           # 0-200 points (transaction volume)
    consistency_score +      # 0-200 points (behavioral consistency)
    diversification_score +  # 0-150 points (asset diversification)
    repayment_score +        # 0-200 points (repayment behavior)
    leverage_score +         # 0-150 points (leverage usage)
    activity_bonus +         # 0-50 points (transaction frequency)
    asset_bonus -            # 0-100 points (unique assets)
    risk_penalty             # 0-200 points (risk indicators)
)
```

- **High scores**: Consistent, diversified, high-volume, and responsible users
- **Low scores**: Inactive, risky, or bot-like wallets

**Score Ranges:**
- 800-1000: Excellent (Highly reliable)
- 600-799: Good (Reliable, minor risks)
- 400-599: Fair (Moderate risk)
- 200-399: Poor (High risk)
- 0-199: Very Poor (Extremely risky)

---

## Usage

### Prerequisites
- Python 3.8+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  # or
  pip install pandas numpy matplotlib seaborn scikit-learn
  ```

### Running the Scoring System
```python
from credit_scoring import DeFiCreditScoring

credit_scorer = DeFiCreditScoring()
results = credit_scorer.generate_scores('user-wallet-transactions.json')
score_ranges = credit_scorer.analyze_results(results)
results.to_csv('wallet_credit_scores.csv', index=False)
```

### Input Format
- JSON file with transaction records, each containing:
  - `userWallet`: Wallet address
  - `action`: Transaction type (deposit, borrow, repay, redeemunderlying, liquidationcall)
  - `timestamp`: Unix timestamp
  - `actionData`: Dict with `amount`, `assetSymbol`, `assetPriceUSD`

### Output
- `wallet_credit_scores.csv`: Wallet addresses, scores, and features
- `analysis.md`: Score distribution, insights, and visualizations
- `score_distribution.png`: Histogram of credit scores

---

## Extensibility
- Add new feature engineering functions easily
- Adjust scoring weights for different risk profiles
- Integrate additional DeFi protocols
- Swap in machine learning models for score prediction

---

## Validation & Transparency
- Each score component is explainable and measurable
- Risk indicators and penalties are clearly defined
- Score ranges correspond to interpretable risk levels
- Feature importance can be analyzed for model improvement

---

## File Structure
```
├── credit_scoring.py         # Main scoring system
├── analysis.md              # Detailed analysis and results
├── wallet_credit_scores.csv # Output scores and features
├── score_distribution.png   # Score distribution plot
├── requirements.txt         # Dependencies
├── README.md                # Project documentation
```

---

## Future Enhancements
- **Machine Learning Integration**: Train supervised models on labeled data
- **Real-time Scoring**: Implement streaming data processing
- **Multi-protocol Support**: Extend to other DeFi protocols
- **Advanced Risk Models**: Incorporate market volatility and liquidity factors
- **Temporal Analysis**: Add time-series features for trend analysis

---

## Example Terminal Output

Below is a sample output from running the scoring system:

```
Loading transaction data...
Preprocessing data...
Engineering features...
Calculating credit scores...

Processed 3497 wallets

Top 5 Highest Scoring Wallets:
                                          wallet  ...  total_usd_volume
2481  0x044c53d8576d4d700e6327c954f88388ee03b8db  ...     321226.242745
727   0x012f15e260f6275bc8e62be475adb07549765e70  ...      16215.715490
2547  0x046a5d95317dbc2ae8ed4a0c370b9183d161a14a  ...      12426.085622
42    0x000c8e2871750f458bf1de8ab528dda09bc95db6  ...      15694.711530
2181  0x03af63559532b015e76b2e70f6940304be09784f  ...      20220.574758

[5 rows x 4 columns]

Top 5 Lowest Scoring Wallets:
                                          wallet  ...  total_usd_volume
2800  0x04dde662ee487ca57b13932a23352eb854ec36bf  ...          0.000108
159   0x003be39433bde975b12411fbc3025d49d813a84f  ...          0.732132
1412  0x0258fefede90decf71000c32412f33726b27d5c0  ...          1.758562
3433  0x05f78c7f3e79c3a6c453d188b013e3812e52cabb  ...          1.094377
1548  0x02948cbed87c7ac0beb2488396a3886b9f656634  ...          0.062782

[5 rows x 4 columns]

=== CREDIT SCORING ANALYSIS ===

Score Distribution Statistics:
Mean Score: 536.59
Median Score: 520.87
Standard Deviation: 135.85
Min Score: 0.00
Max Score: 871.15

Score Range Distribution:
0-100: 2 wallets (0.1%)
100-200: 4 wallets (0.1%)
200-300: 92 wallets (2.6%)
300-400: 184 wallets (5.3%)
400-500: 1313 wallets (37.5%)
500-600: 719 wallets (20.6%)
600-700: 646 wallets (18.5%)
700-800: 476 wallets (13.6%)
800-900: 61 wallets (1.7%)
900-1000: 0 wallets (0.0%)

Low Score Wallets Analysis (Score < 300): 98 wallets
Average transactions: 3.07
Average USD volume: $134541.37
Average risk indicators: 0.009

High Score Wallets Analysis (Score >= 700): 537 wallets
Average transactions: 76.64
Average USD volume: $1642989.10
Average consistency: 0.134

Results saved to 'wallet_credit_scores.csv'
``` 
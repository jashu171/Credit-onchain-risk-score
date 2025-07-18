import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('wallet_credit_scores.csv')
plt.figure(figsize=(10,6))
plt.hist(df['credit_score'], bins=range(0, 1100, 100), edgecolor='black')
plt.title('Wallet Credit Score Distribution')
plt.xlabel('Credit Score')
plt.ylabel('Number of Wallets')
plt.grid(axis='y')
plt.show()
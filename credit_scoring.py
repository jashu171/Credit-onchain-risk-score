import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class DeFiCreditScoring:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.feature_columns = []
        
    def load_data(self, json_file_path):
        """Load transaction data from JSON file"""
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def preprocess_data(self, df):
        """Clean and preprocess the transaction data"""
        # Convert timestamp to datetime
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Extract amount as float
        df['amount_float'] = df['actionData'].apply(lambda x: float(x.get('amount', 0)))
        df['asset_price_usd'] = df['actionData'].apply(lambda x: float(x.get('assetPriceUSD', 0)))
        df['asset_symbol'] = df['actionData'].apply(lambda x: x.get('assetSymbol', ''))
        
        # Calculate USD value of transaction
        df['usd_value'] = df['amount_float'] * df['asset_price_usd']
        
        # Handle different asset decimals (common DeFi tokens)
        decimal_mapping = {
            'USDC': 6, 'USDT': 6, 'WBTC': 8, 'WETH': 18, 'WMATIC': 18, 'DAI': 18
        }
        
        def adjust_for_decimals(row):
            decimals = decimal_mapping.get(row['asset_symbol'], 18)
            return row['amount_float'] / (10 ** decimals)
        
        df['adjusted_amount'] = df.apply(adjust_for_decimals, axis=1)
        df['adjusted_usd_value'] = df['adjusted_amount'] * df['asset_price_usd']
        
        return df
    
    def engineer_features(self, df):
        """Engineer features for credit scoring"""
        wallet_features = {}
        
        for wallet in df['userWallet'].unique():
            wallet_data = df[df['userWallet'] == wallet].copy()
            wallet_data = wallet_data.sort_values('timestamp')
            
            features = {}
            
            # Basic transaction metrics
            features['total_transactions'] = len(wallet_data)
            features['unique_assets'] = wallet_data['asset_symbol'].nunique()
            features['total_usd_volume'] = wallet_data['adjusted_usd_value'].sum()
            features['avg_transaction_size'] = wallet_data['adjusted_usd_value'].mean()
            features['median_transaction_size'] = wallet_data['adjusted_usd_value'].median()
            
            # Action distribution
            action_counts = wallet_data['action'].value_counts()
            total_actions = len(wallet_data)
            features['deposit_ratio'] = action_counts.get('deposit', 0) / total_actions
            features['borrow_ratio'] = action_counts.get('borrow', 0) / total_actions
            features['repay_ratio'] = action_counts.get('repay', 0) / total_actions
            features['redeem_ratio'] = action_counts.get('redeemunderlying', 0) / total_actions
            features['liquidation_ratio'] = action_counts.get('liquidationcall', 0) / total_actions
            
            # Time-based features
            time_span = wallet_data['timestamp'].max() - wallet_data['timestamp'].min()
            features['activity_duration_days'] = time_span / (24 * 3600)
            features['transaction_frequency'] = features['total_transactions'] / max(features['activity_duration_days'], 1)
            
            # Behavioral patterns
            features['consistent_usage'] = self.calculate_consistency(wallet_data)
            features['risk_indicators'] = self.calculate_risk_indicators(wallet_data)
            features['diversification_score'] = self.calculate_diversification(wallet_data)
            
            # Financial health indicators
            features['leverage_indicator'] = self.calculate_leverage_indicator(wallet_data)
            features['repayment_behavior'] = self.calculate_repayment_behavior(wallet_data)
            
            wallet_features[wallet] = features
        
        return pd.DataFrame.from_dict(wallet_features, orient='index')
    
    def calculate_consistency(self, wallet_data):
        """Calculate consistency score based on transaction patterns"""
        if len(wallet_data) < 2:
            return 0.5
        
        # Check for regular time intervals
        time_diffs = np.diff(sorted(wallet_data['timestamp']))
        time_consistency = 1 - (np.std(time_diffs) / (np.mean(time_diffs) + 1e-10))
        
        # Check for consistent transaction sizes
        size_consistency = 1 - (wallet_data['adjusted_usd_value'].std() / (wallet_data['adjusted_usd_value'].mean() + 1e-10))
        
        return np.clip((time_consistency + size_consistency) / 2, 0, 1)
    
    def calculate_risk_indicators(self, wallet_data):
        """Calculate risk indicators (lower is better)"""
        risk_score = 0
        
        # High frequency in short time (potential bot behavior)
        if len(wallet_data) > 10:
            time_span = wallet_data['timestamp'].max() - wallet_data['timestamp'].min()
            if time_span < 3600:  # Less than 1 hour
                risk_score += 0.3
        
        # Unusual transaction patterns
        if wallet_data['adjusted_usd_value'].std() > wallet_data['adjusted_usd_value'].mean() * 5:
            risk_score += 0.2
        
        # Only liquidation calls
        if (wallet_data['action'] == 'liquidationcall').all():
            risk_score += 0.5
        
        return np.clip(risk_score, 0, 1)
    
    def calculate_diversification(self, wallet_data):
        """Calculate asset diversification score"""
        unique_assets = wallet_data['asset_symbol'].nunique()
        total_transactions = len(wallet_data)
        
        if total_transactions == 0:
            return 0
        
        # Shannon entropy for asset distribution
        asset_counts = wallet_data['asset_symbol'].value_counts()
        probabilities = asset_counts / total_transactions
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        
        # Normalize entropy (log2 of max possible outcomes)
        max_entropy = np.log2(min(unique_assets, 10))  # Cap at 10 for normalization
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        return np.clip(normalized_entropy, 0, 1)
    
    def calculate_leverage_indicator(self, wallet_data):
        """Calculate leverage usage indicator"""
        borrows = wallet_data[wallet_data['action'] == 'borrow']['adjusted_usd_value'].sum()
        deposits = wallet_data[wallet_data['action'] == 'deposit']['adjusted_usd_value'].sum()
        
        if deposits == 0:
            return 0 if borrows == 0 else -1  # Borrowing without deposits is risky
        
        leverage_ratio = borrows / deposits
        # Convert to score (moderate leverage is good, excessive is bad)
        if leverage_ratio <= 0.5:
            return 0.8  # Conservative
        elif leverage_ratio <= 1.0:
            return 1.0  # Optimal
        elif leverage_ratio <= 2.0:
            return 0.6  # Moderate risk
        else:
            return 0.2  # High risk
    
    def calculate_repayment_behavior(self, wallet_data):
        """Calculate repayment behavior score"""
        borrows = wallet_data[wallet_data['action'] == 'borrow']['adjusted_usd_value'].sum()
        repays = wallet_data[wallet_data['action'] == 'repay']['adjusted_usd_value'].sum()
        
        if borrows == 0:
            return 0.8  # No borrowing is neutral
        
        repayment_ratio = repays / borrows
        return np.clip(repayment_ratio, 0, 1)
    
    def calculate_credit_score(self, features_df):
        """Calculate final credit score based on engineered features"""
        scores = {}
        
        for wallet in features_df.index:
            features = features_df.loc[wallet]
            
            # Base score components
            volume_score = min(np.log10(features['total_usd_volume'] + 1) / 5, 1) * 200
            consistency_score = features['consistent_usage'] * 200
            diversification_score = features['diversification_score'] * 150
            repayment_score = features['repayment_behavior'] * 200
            leverage_score = features['leverage_indicator'] * 150
            
            # Penalty for risk indicators
            risk_penalty = features['risk_indicators'] * 200
            
            # Bonus for good behavior
            activity_bonus = min(features['transaction_frequency'] * 10, 50)
            asset_bonus = min(features['unique_assets'] * 20, 100)
            
            # Calculate final score
            final_score = (
                volume_score + consistency_score + diversification_score + 
                repayment_score + leverage_score + activity_bonus + asset_bonus - risk_penalty
            )
            
            # Normalize to 0-1000 range
            final_score = np.clip(final_score, 0, 1000)
            scores[wallet] = final_score
        
        return scores
    
    def generate_scores(self, json_file_path):
        """Main function to generate credit scores from JSON file"""
        print("Loading transaction data...")
        df = self.load_data(json_file_path)
        if df is None:
            return None
        
        print("Preprocessing data...")
        df = self.preprocess_data(df)
        
        print("Engineering features...")
        features_df = self.engineer_features(df)
        
        print("Calculating credit scores...")
        scores = self.calculate_credit_score(features_df)
        
        # Create results dataframe
        results_df = pd.DataFrame({
            'wallet': list(scores.keys()),
            'credit_score': list(scores.values())
        })
        
        # Add feature data
        results_df = results_df.set_index('wallet').join(features_df)
        results_df = results_df.reset_index()
        
        return results_df
    
    def analyze_results(self, results_df):
        """Analyze and visualize the credit scoring results"""
        print("\n=== CREDIT SCORING ANALYSIS ===\n")
        
        # Basic statistics
        print("Score Distribution Statistics:")
        print(f"Mean Score: {results_df['credit_score'].mean():.2f}")
        print(f"Median Score: {results_df['credit_score'].median():.2f}")
        print(f"Standard Deviation: {results_df['credit_score'].std():.2f}")
        print(f"Min Score: {results_df['credit_score'].min():.2f}")
        print(f"Max Score: {results_df['credit_score'].max():.2f}")
        
        # Score ranges
        score_ranges = {
            '0-100': len(results_df[(results_df['credit_score'] >= 0) & (results_df['credit_score'] < 100)]),
            '100-200': len(results_df[(results_df['credit_score'] >= 100) & (results_df['credit_score'] < 200)]),
            '200-300': len(results_df[(results_df['credit_score'] >= 200) & (results_df['credit_score'] < 300)]),
            '300-400': len(results_df[(results_df['credit_score'] >= 300) & (results_df['credit_score'] < 400)]),
            '400-500': len(results_df[(results_df['credit_score'] >= 400) & (results_df['credit_score'] < 500)]),
            '500-600': len(results_df[(results_df['credit_score'] >= 500) & (results_df['credit_score'] < 600)]),
            '600-700': len(results_df[(results_df['credit_score'] >= 600) & (results_df['credit_score'] < 700)]),
            '700-800': len(results_df[(results_df['credit_score'] >= 700) & (results_df['credit_score'] < 800)]),
            '800-900': len(results_df[(results_df['credit_score'] >= 800) & (results_df['credit_score'] < 900)]),
            '900-1000': len(results_df[(results_df['credit_score'] >= 900) & (results_df['credit_score'] <= 1000)])
        }
        
        print("\nScore Range Distribution:")
        for range_name, count in score_ranges.items():
            percentage = (count / len(results_df)) * 100
            print(f"{range_name}: {count} wallets ({percentage:.1f}%)")
        
        # Analyze low score wallets (0-300)
        low_score_wallets = results_df[results_df['credit_score'] < 300]
        print(f"\nLow Score Wallets Analysis (Score < 300): {len(low_score_wallets)} wallets")
        if len(low_score_wallets) > 0:
            print(f"Average transactions: {low_score_wallets['total_transactions'].mean():.2f}")
            print(f"Average USD volume: ${low_score_wallets['total_usd_volume'].mean():.2f}")
            print(f"Average risk indicators: {low_score_wallets['risk_indicators'].mean():.3f}")
        
        # Analyze high score wallets (700+)
        high_score_wallets = results_df[results_df['credit_score'] >= 700]
        print(f"\nHigh Score Wallets Analysis (Score >= 700): {len(high_score_wallets)} wallets")
        if len(high_score_wallets) > 0:
            print(f"Average transactions: {high_score_wallets['total_transactions'].mean():.2f}")
            print(f"Average USD volume: ${high_score_wallets['total_usd_volume'].mean():.2f}")
            print(f"Average consistency: {high_score_wallets['consistent_usage'].mean():.3f}")
        
        return score_ranges

# Example usage
if __name__ == "__main__":
    # Initialize the credit scoring system
    credit_scorer = DeFiCreditScoring()
    
    # Process the JSON file (replace with your actual file path)
    json_file_path = "user-wallet-transactions.json"  # Your provided sample file
    
    # Generate scores
    results = credit_scorer.generate_scores(json_file_path)
    
    if results is not None:
        print(f"\nProcessed {len(results)} wallets")
        print("\nTop 5 Highest Scoring Wallets:")
        print(results.nlargest(5, 'credit_score')[['wallet', 'credit_score', 'total_transactions', 'total_usd_volume']])
        
        print("\nTop 5 Lowest Scoring Wallets:")
        print(results.nsmallest(5, 'credit_score')[['wallet', 'credit_score', 'total_transactions', 'total_usd_volume']])
        
        # Analyze results
        score_ranges = credit_scorer.analyze_results(results)
        
        # Save results
        results.to_csv('wallet_credit_scores.csv', index=False)
        print("\nResults saved to 'wallet_credit_scores.csv'")
    else:
        print("Failed to process the data")
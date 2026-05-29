import argparse
import sys
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, association_rules

def run_pattern_mining(file_path, min_support=0.03):
    """
    Executes FP-Growth algorithm on the cleaned GTD dataset.
    Incorporates CLI arguments, strict dtype definitions, and robust error handling.
    """
    print("--- Loading Cleaned Dataset ---")
    
    mining_cols = [
        'region_txt', 
        'attacktype1_txt', 
        'weaptype1_txt', 
        'targtype1_txt', 
        'success',
        'casualty_level',
        'decade'
    ]
    
    # Performance Optimization: Explicit dtypes to avoid memory spikes and low_memory=False
    col_dtypes = {
        'region_txt': 'category',
        'attacktype1_txt': 'category',
        'weaptype1_txt': 'category',
        'targtype1_txt': 'category',
        'success': 'float32',
        'casualty_level': 'category',
        'decade': 'category'
    }

    # Maintainability: Robust error handling for file reading
    try:
        df_clean = pd.read_csv(file_path, usecols=mining_cols, dtype=col_dtypes)
    except FileNotFoundError:
        print(f"Error: Dataset not found at path: {file_path}")
        print("Please ensure the ETL script has been executed and the file exists.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        sys.exit(1)
    
    # Data Logic Bug Fix: Vectorized mapping to handle NaN or -9 code properly
    df_clean['success'] = df_clean['success'].map({1.0: 'Success', 0.0: 'Failed'}).fillna('Unknown')
    
    print(f"Successfully loaded {df_clean.shape[0]} clean rows for association mining.")

    print("\n--- One-Hot Encoding Conversion ---")
    df_onehot = pd.get_dummies(df_clean, columns=mining_cols).astype(bool)
    print(f"One-hot matrix shape generated: {df_onehot.shape}")

    print("\n--- Extracting Frequent Itemsets (FP-Growth) ---")
    frequent_itemsets = fpgrowth(df_onehot, min_support=min_support, use_colnames=True)
    print(f"Identified {frequent_itemsets.shape[0]} frequent itemsets.")

    print("\n--- Generating and Filtering Association Rules ---")
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
    
    # Strict constraint enforcement
    filtered_rules = rules[rules['lift'] > 1.5].copy()
    filtered_rules = filtered_rules.sort_values(by=['lift', 'confidence'], ascending=False)
    
    # Pipeline Breaker Fix: Convert frozenset to comma-separated strings for CSV integrity
    filtered_rules['antecedents'] = filtered_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
    filtered_rules['consequents'] = filtered_rules['consequents'].apply(lambda x: ', '.join(list(x)))
    
    print(f"Discovered {filtered_rules.shape[0]} rules satisfying the constraint: Lift > 1.5")
    
    return filtered_rules

if __name__ == "__main__":
    # Maintainability: Implementing argparse for dynamic CLI execution
    parser = argparse.ArgumentParser(description="Run FP-Growth Pattern Mining for Task T03-B")
    parser.add_argument("--input", type=str, default="../../data/processed/gtd_cleaned.csv", help="Path to the cleaned dataset")
    parser.add_argument("--output", type=str, default="../gtd_discovered_rules.csv", help="Path to save the output rules CSV")
    parser.add_argument("--min_support", type=float, default=0.03, help="Minimum support threshold for FP-Growth")
    
    args = parser.parse_args()
    
    final_rules = run_pattern_mining(args.input, args.min_support)
    
    print("\n--- Top 15 Highly-Correlated Tactical Rules (Lift > 1.5) ---")
    preview_cols = ['antecedents', 'consequents', 'support', 'confidence', 'lift']
    print(final_rules[preview_cols].head(15).to_string())
    
    final_rules.to_csv(args.output, index=False)
    print(f"\nRules successfully exported and saved to '{args.output}'")
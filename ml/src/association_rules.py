
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, association_rules

def run_pattern_mining(file_path, min_support=0.03):
    """
    Executes FP-Growth algorithm on the cleaned dataset provided by Duy Hoang (T01-A).
    Incorporates advanced discretized features for richer insight generation.
    """
    print("--- Loading Cleaned Dataset ---")
    # Selection of core and advanced discretized features from Hoang's output
    mining_cols = [
        'region_txt', 
        'attacktype1_txt', 
        'weaptype1_txt', 
        'targtype1_txt', 
        'success',
        'casualty_level',   # Discretized casualties added by Hoang
        'decade'            # Discretized time periods added by Hoang
    ]
    
    df_clean = pd.read_csv(file_path, usecols=mining_cols, low_memory=False)
    
    # Standardize success label text
    df_clean['success'] = df_clean['success'].apply(lambda x: 'Success' if x == 1.0 else 'Failed')
    print(f"Successfully loaded {df_clean.shape[0]} clean rows for association mining.")

    print("\n--- One-Hot Encoding Conversion ---")
    # Transform categorical values into binary matrix format
    df_onehot = pd.get_dummies(df_clean, columns=mining_cols).astype(bool)
    print(f"One-hot matrix shape generated: {df_onehot.shape}")

    print("\n--- Extracting Frequent Itemsets (FP-Growth) ---")
    # Explicitly using FP-Growth instead of Apriori per TAD requirements
    frequent_itemsets = fpgrowth(df_onehot, min_support=min_support, use_colnames=True)
    print(f"Identified {frequent_itemsets.shape[0]} frequent itemsets.")

    print("\n--- Generating and Filtering Association Rules ---")
    # Compute association rules based on confidence metric
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
    
    # STRICT RULE FROM TAD: Filter only rules where Lift > 1.5 (Must-Link constraints)
    filtered_rules = rules[rules['lift'] > 1.5].copy()
    
    # Sort by impact metrics for analytical priority
    filtered_rules = filtered_rules.sort_values(by=['lift', 'confidence'], ascending=False)
    print(f"Discovered {filtered_rules.shape[0]} rules satisfying the constraint: Lift > 1.5")
    
    return filtered_rules

if __name__ == "__main__":
    # Relative path pointing to the clean data directory
    cleaned_dataset_path = '../../data/processed/gtd_cleaned.csv'
    
    # Execute mining script (min_support set to 3% for robust patterns across 203k rows)
    final_rules = run_pattern_mining(cleaned_dataset_path, min_support=0.03)
    
    print("\n--- Top 15 Highly-Correlated Tactical Rules (Lift > 1.5) ---")
    preview_cols = ['antecedents', 'consequents', 'support', 'confidence', 'lift']
    print(final_rules[preview_cols].head(15).to_string())
    
    # Export rules to serve as Must-Link constraints for Task T04-B (Clustering)
    output_path = '../gtd_discovered_rules.csv'
    final_rules.to_csv(output_path, index=False)
    print(f"\nRules successfully exported and saved to '{output_path}'")
import os
import time
import json
import pandas as pd
from pathlib import Path
from mlxtend.frequent_patterns import fpgrowth, association_rules

# Thiết lập đường dẫn (Tương tự file gốc)
BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = BASE_DIR / "ml"
MODELS_DIR = ML_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_PATH = BASE_DIR / "data" / "processed" / "outputs_t01" / "gtd_cleaned.csv"

def run_fp_growth(df: pd.DataFrame):
    print("--- 1. Pattern Mining (FP-Growth) ---")
    cols = ['attacktype1_txt', 'targtype1_txt', 'weaptype1_txt', 'region_txt']
    
    print(f"Selecting categorical columns: {cols}")
    data = df[cols].dropna().copy()
    
    # Tạo items phân biệt để tránh trùng lặp tên
    for col in cols:
        data[col] = col + "=" + data[col].astype(str)
        
    print("Converting to transaction list...")
    transactions = data.values.tolist()
    
    from mlxtend.preprocessing import TransactionEncoder
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df_trans = pd.DataFrame(te_ary, columns=te.columns_)
    
    print("Running FP-Growth (min_support=0.05)...")
    start = time.time()
    frequent_itemsets = fpgrowth(df_trans, min_support=0.05, use_colnames=True)
    
    print("Extracting Association Rules (min_lift=1.5)...")
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.5)
    
    print(f"Found {len(rules)} rules.")
    
    if not rules.empty:
        # Lọc luật 1-kéo-theo-1 (Antecedents = 1, Consequents = 1)
        rules['ant_len'] = rules['antecedents'].apply(len)
        rules['con_len'] = rules['consequents'].apply(len)
        simple_rules = rules[(rules['ant_len'] == 1) & (rules['con_len'] == 1)]
        
        if not simple_rules.empty:
            simple_rules = simple_rules.sort_values(by=['lift', 'confidence'], ascending=False)
            best_rule = simple_rules.iloc[0]
            
            # Lưu danh sách luật ra CSV
            rules_path = MODELS_DIR / "fp_growth_rules.csv"
            rules.to_csv(rules_path, index=False)
            print(f"Rules saved to {rules_path}")
            
            # Xuất ràng buộc mạnh nhất ra file JSON để Script sau (Clustering) sử dụng
            rule_data = {
                "antecedents": list(best_rule['antecedents']),
                "consequents": list(best_rule['consequents']),
                "lift": float(best_rule['lift'])
            }
            json_path = MODELS_DIR / "must_link_rule.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(rule_data, f, indent=4)
                
            print(f"🔥 Best Rule (Must-Link) saved to {json_path}:")
            print(f"   {rule_data['antecedents']} -> {rule_data['consequents']} (Lift: {rule_data['lift']:.2f})")
            
            print(f"FP-Growth completed in {time.time() - start:.1f}s\n")
    return rule_data
            
    print("No strong simple rules found.")
    return None

def main():
    if not DATA_PATH.exists():
        print(f"Error: Dataset {DATA_PATH} not found.")
        return
        
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH, low_memory=False)
    
    run_fp_growth(df)

if __name__ == "__main__":
    main()
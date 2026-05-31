import os
import time
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from mlxtend.frequent_patterns import fpgrowth, association_rules
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, roc_curve, auc, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = BASE_DIR / "ml"
MODELS_DIR = ML_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_PATH = BASE_DIR / "data" / "processed" / "outputs_t01" / "gtd_cleaned.csv"


def run_fp_growth(df: pd.DataFrame) -> pd.DataFrame:
    print("--- 1. Pattern Mining (FP-Growth) ---")
    cols = ['attacktype1_txt', 'targtype1_txt', 'weaptype1_txt', 'region_txt']
    
    print(f"Selecting categorical columns: {cols}")
    data = df[cols].dropna().copy()
    
    # Create distinct items to avoid overlapping names
    for col in cols:
        data[col] = col + "_" + data[col].astype(str)
        
    print("Converting to boolean dataframe (one-hot encoding)...")
    basket = pd.get_dummies(data, prefix="", prefix_sep="")
    basket = basket.astype(bool)
    
    print("Running FP-Growth (min_support=0.01)...")
    start = time.time()
    frequent_itemsets = fpgrowth(basket, min_support=0.01, use_colnames=True)
    print(f"Found {len(frequent_itemsets)} frequent itemsets.")
    
    print("Extracting Association Rules...")
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.5)
    rules = rules.sort_values('lift', ascending=False)
    
    out_file = BASE_DIR / "data" / "processed" / "fp_growth_rules.csv"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Format rules for better readability in CSV
    def format_frozen(fs):
        return ", ".join(list(fs))
        
    rules_export = rules.copy()
    rules_export['antecedents'] = rules_export['antecedents'].apply(format_frozen)
    rules_export['consequents'] = rules_export['consequents'].apply(format_frozen)
    rules_export.to_csv(out_file, index=False)
    
    print(f"Extracted {len(rules)} rules with lift > 1.5. Saved to {out_file}")
    print(f"FP-Growth completed in {time.time() - start:.1f}s\n")
    return rules


def run_classification(df: pd.DataFrame):
    print("--- 2. Classification Model (XGBoost vs Random Forest) ---")
    feature_cols = ['iyear', 'region', 'country', 'attacktype1', 'targtype1', 'weaptype1']
    target_col = 'success'
    
    data = df[feature_cols + [target_col]].copy()
    data = data.dropna(subset=[target_col])
    data[target_col] = data[target_col].astype(int)
    
    # Fill missing numeric values with -1
    data = data.fillna(-1)
    
    X = data[feature_cols]
    y = data[target_col]
    
    print(f"Dataset shape: {X.shape}")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Calculate scale_pos_weight to handle class imbalance
    neg_cases = (y_train == 0).sum()
    pos_cases = (y_train == 1).sum()
    scale_pos_weight = neg_cases / pos_cases if pos_cases > 0 else 1.0
    
    print(f"Class imbalance handling - scale_pos_weight: {scale_pos_weight:.2f}")
    
    xgb_model = XGBClassifier(
        n_estimators=100, max_depth=6, scale_pos_weight=scale_pos_weight, random_state=42, eval_metric="logloss"
    )
    
    rf_model = RandomForestClassifier(
        n_estimators=100, max_depth=10, class_weight="balanced", random_state=42
    )
    
    start = time.time()
    print("Training XGBoost Classifier...")
    xgb_model.fit(X_train, y_train)
    print("Training Random Forest Classifier (Baseline)...")
    rf_model.fit(X_train, y_train)
    print(f"Training completed in {time.time() - start:.1f}s\n")
    
    print("Evaluating Models...")
    evaluate_and_report_models(xgb_model, rf_model, X_test, y_test)
    
    model_path = MODELS_DIR / "xgboost_classifier.pkl"
    joblib.dump(xgb_model, model_path)
    print(f"Advanced Model (XGBoost) saved to {model_path}\n")
    return xgb_model

def evaluate_and_report_models(xgb_model, rf_model, X_test, y_test):
    # Predict
    xgb_pred = xgb_model.predict(X_test)
    xgb_prob = xgb_model.predict_proba(X_test)[:, 1]
    rf_pred = rf_model.predict(X_test)
    rf_prob = rf_model.predict_proba(X_test)[:, 1]
    
    # Metrics
    metrics = {
        "XGBoost": {
            "Accuracy": accuracy_score(y_test, xgb_pred),
            "Precision": precision_score(y_test, xgb_pred, zero_division=0),
            "Recall": recall_score(y_test, xgb_pred, zero_division=0),
            "F1-Score": f1_score(y_test, xgb_pred, zero_division=0)
        },
        "Random Forest": {
            "Accuracy": accuracy_score(y_test, rf_pred),
            "Precision": precision_score(y_test, rf_pred, zero_division=0),
            "Recall": recall_score(y_test, rf_pred, zero_division=0),
            "F1-Score": f1_score(y_test, rf_pred, zero_division=0)
        }
    }
    
    # 1. Plot ROC Curve
    fpr_xgb, tpr_xgb, _ = roc_curve(y_test, xgb_prob)
    auc_xgb = auc(fpr_xgb, tpr_xgb)
    
    fpr_rf, tpr_rf, _ = roc_curve(y_test, rf_prob)
    auc_rf = auc(fpr_rf, tpr_rf)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr_xgb, tpr_xgb, color='darkorange', lw=2, label=f'XGBoost (AUC = {auc_xgb:.4f})')
    plt.plot(fpr_rf, tpr_rf, color='blue', lw=2, label=f'Random Forest (AUC = {auc_rf:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC Curve)')
    plt.legend(loc="lower right")
    
    roc_path = BASE_DIR / "data" / "processed" / "roc_curve.png"
    plt.savefig(roc_path)
    plt.close()
    
    # 2. Plot Confusion Matrix for XGBoost
    cm = confusion_matrix(y_test, xgb_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Failure (0)', 'Success (1)'], yticklabels=['Failure (0)', 'Success (1)'])
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix - XGBoost Model')
    
    cm_path = BASE_DIR / "data" / "processed" / "confusion_matrix.png"
    plt.savefig(cm_path)
    plt.close()
    
    # 3. Export Automated Markdown Report
    report_path = BASE_DIR / "data" / "processed" / "ML_Evaluation_Report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 📊 BÁO CÁO ĐÁNH GIÁ MÔ HÌNH MACHINE LEARNING (AUTOMATED)\n\n")
        f.write("Báo cáo được tự động tạo từ script `03_data_mining.py` sau quá trình huấn luyện mô hình.\n\n")
        
        f.write("## 1. So sánh Mô hình (Baseline Comparison)\n")
        f.write("| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |\n")
        f.write("|-------|----------|-----------|--------|----------|---------|\n")
        f.write(f"| **XGBoost (Advanced)** | {metrics['XGBoost']['Accuracy']:.4f} | {metrics['XGBoost']['Precision']:.4f} | {metrics['XGBoost']['Recall']:.4f} | {metrics['XGBoost']['F1-Score']:.4f} | **{auc_xgb:.4f}** |\n")
        f.write(f"| **Random Forest (Baseline)** | {metrics['Random Forest']['Accuracy']:.4f} | {metrics['Random Forest']['Precision']:.4f} | {metrics['Random Forest']['Recall']:.4f} | {metrics['Random Forest']['F1-Score']:.4f} | {auc_rf:.4f} |\n\n")
        
        f.write("## 2. Biểu đồ ROC Curve\n")
        f.write("Biểu đồ so sánh đường cong ROC giữa XGBoost và thuật toán Baseline (Random Forest):\n\n")
        f.write("![ROC Curve](./roc_curve.png)\n\n")
        
        f.write("## 3. Ma trận nhầm lẫn (Confusion Matrix)\n")
        f.write("Ma trận nhầm lẫn của mô hình XGBoost tốt nhất trên tập Test, cho thấy tỷ lệ False Positive và False Negative:\n\n")
        f.write("![Confusion Matrix](./confusion_matrix.png)\n\n")
        
    print(f"Generated ROC Curve: {roc_path}")
    print(f"Generated Confusion Matrix: {cm_path}")
    print(f"Generated Evaluation Report: {report_path}")


def run_clustering(df: pd.DataFrame, rules: pd.DataFrame):
    print("--- 3. Clustering Model (COP-KMeans logic with Must-Link) ---")
    
    # We sample the dataset to avoid excessive computation times for clustering
    sample_size = 10000
    print(f"Sampling {sample_size} instances for clustering...")
    sample_df = df.sample(n=sample_size, random_state=42).copy()
    
    cluster_cols = ['iyear', 'region', 'attacktype1', 'targtype1', 'weaptype1']
    X_clust = sample_df[cluster_cols].fillna(-1)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clust)
    
    # Find instances satisfying the top MUST-LINK rule
    print("Extracting Must-Link constraints from Top FP-Growth Rule...")
    top_rule = None
    match_idx = []
    
    if not rules.empty:
        top_rule = rules.iloc[0]
        ant = list(top_rule['antecedents'])[0]
        con = list(top_rule['consequents'])[0]
        print(f"Top Rule: {ant} => {con} (Lift: {top_rule['lift']:.2f})")
        
        # Parse the actual values
        ant_val = ant.split("_", 1)[1] if "_" in ant else ant
        con_val = con.split("_", 1)[1] if "_" in con else con
        
        text_series = (sample_df['attacktype1_txt'].astype(str) + " " +
                       sample_df['targtype1_txt'].astype(str) + " " +
                       sample_df['weaptype1_txt'].astype(str) + " " +
                       sample_df['region_txt'].astype(str))
                       
        match_idx = sample_df[text_series.str.contains(ant_val, regex=False) & 
                              text_series.str.contains(con_val, regex=False)].index
    
    print(f"Found {len(match_idx)} instances satisfying this rule.")
    
    # Implement COP-KMeans Must-Link equivalent logic:
    # Instead of O(N^2) pairwise constraints, instances that MUST link are aggregated 
    # to form a strong "anchor" point representing that tactical pattern.
    
    if len(match_idx) > 1:
        print(f"Aggregating {len(match_idx)} Must-Link instances into a structural anchor...")
        # Get positions of these indices
        positions = [sample_df.index.get_loc(idx) for idx in match_idx]
        
        # Calculate centroid of the must-link group
        ml_centroid = X_scaled[positions].mean(axis=0).reshape(1, -1)
        
        # Remove original must-link points and add the weighted centroid
        X_reduced = np.delete(X_scaled, positions, axis=0)
        X_final = np.vstack([X_reduced, ml_centroid])
        
        # Weights: 1 for normal points, len(match_idx) for the anchor
        weights = np.ones(len(X_final))
        weights[-1] = len(match_idx)
    else:
        X_final = X_scaled
        weights = np.ones(len(X_final))
        
    print(f"Running KMeans on {len(X_final)} points (with constraints handled via anchor weighting)...")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    
    start = time.time()
    kmeans.fit(X_final, sample_weight=weights)
    
    # Predict clusters for original data
    sample_df['cluster'] = kmeans.predict(X_scaled)
    
    print("Cluster distribution:")
    print(sample_df['cluster'].value_counts().sort_index())
    
    model_path = MODELS_DIR / "cop_kmeans.pkl"
    scaler_path = MODELS_DIR / "cop_kmeans_scaler.pkl"
    joblib.dump(kmeans, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"Clustering model saved to {model_path}")
    print(f"Clustering completed in {time.time() - start:.1f}s\n")


def main():
    if not DATA_PATH.exists():
        print(f"Error: Dataset {DATA_PATH} not found. Please run ETL scripts first.")
        return
        
    print("Loading cleaned dataset...")
    df = pd.read_csv(DATA_PATH, low_memory=False)
    
    # 1. Pattern Mining
    rules = run_fp_growth(df)
    
    # 2. Classification
    run_classification(df)
    
    # 3. Clustering
    run_clustering(df, rules)


if __name__ == "__main__":
    main()

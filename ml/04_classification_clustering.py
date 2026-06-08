import os
import time
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, roc_curve, auc, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

# Thiết lập đường dẫn
BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = BASE_DIR / "ml"
MODELS_DIR = ML_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_PATH = BASE_DIR / "data" / "processed" / "outputs_t01" / "gtd_cleaned.csv"
RULE_PATH = MODELS_DIR / "must_link_rule.json"

def run_classification(df: pd.DataFrame):
    print("--- 2. Classification (Predicting 'success') ---")
    if 'success' not in df.columns:
        print("Column 'success' not found.")
        return
        
    features = ['iyear', 'imonth', 'iday', 'extended', 'region', 'attacktype1', 'targtype1', 'weaptype1', 'nkill', 'nwound']
    df_model = df.dropna(subset=['success'] + features).copy()
    
    X = df_model[features]
    y = df_model['success']
    
    print(f"Dataset shape for classification: {X.shape}")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Random Forest
    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_probs = rf.predict_proba(X_test)[:, 1]
    
    # XGBoost
    print("Training XGBoost...")
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42, n_jobs=-1)
    xgb.fit(X_train, y_train)
    xgb_preds = xgb.predict(X_test)
    xgb_probs = xgb.predict_proba(X_test)[:, 1]
    
    print("\n[Random Forest Metrics]")
    print(classification_report(y_test, rf_preds))
    print("\n[XGBoost Metrics]")
    print(classification_report(y_test, xgb_preds))
    
    # Lưu Model
    joblib.dump(rf, MODELS_DIR / "random_forest.pkl")
    joblib.dump(xgb, MODELS_DIR / "xgboost.pkl")
    print("Models saved.")
    
    # Vẽ biểu đồ ROC
    fpr_rf, tpr_rf, _ = roc_curve(y_test, rf_probs)
    fpr_xgb, tpr_xgb, _ = roc_curve(y_test, xgb_probs)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr_rf, tpr_rf, label=f"Random Forest (AUC = {auc(fpr_rf, tpr_rf):.2f})")
    plt.plot(fpr_xgb, tpr_xgb, label=f"XGBoost (AUC = {auc(fpr_xgb, tpr_xgb):.2f})")
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    plot_path = MODELS_DIR / "roc_curve.png"
    plt.savefig(plot_path)
    print(f"ROC curve saved to {plot_path}\n")
def run_clustering(df: pd.DataFrame, must_link_rule: dict = None):
    print("--- 3. Clustering (COP-KMeans with Must-Link) ---")
    
    num_cols = ['nkill', 'nwound', 'iyear']
    cat_cols = ['attacktype1_txt', 'weaptype1_txt']
    
    sample_df = df.dropna(subset=num_cols + cat_cols).sample(n=10000, random_state=42).copy()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(sample_df[num_cols])
    
    if must_link_rule is not None:
        print("Applying Must-Link constraint using Penalty Weight...")
        ant = must_link_rule['antecedents'][0]
        con = must_link_rule['consequents'][0]
        
        ant_col, ant_val = ant.split("=")
        con_col, con_val = con.split("=")
        
        match_idx = sample_df[(sample_df[ant_col].astype(str) == ant_val) & 
                              (sample_df[con_col].astype(str) == con_val)].index
                              
        print(f"Found {len(match_idx)} samples satisfying the Must-Link rule.")
        
        # Soft-Constraint: Tính toán centroid của các điểm thỏa mãn luật và kéo chúng lại
        target_pts = X_scaled[sample_df.index.isin(match_idx)]
        if len(target_pts) > 0:
            ideal_centroid = target_pts.mean(axis=0)
            # Thêm một "tâm lực hút" ảo
            X_final = np.vstack([X_scaled, ideal_centroid])
            
            # Trọng số: 1 cho điểm bình thường, lớn hơn cho điểm neo
            weights = np.ones(len(X_final))
            weights[-1] = len(match_idx)
        else:
            X_final = X_scaled
            weights = np.ones(len(X_final))
    else:
        print("No Must-Link rule provided. Running standard KMeans.")
        X_final = X_scaled
        weights = np.ones(len(X_final))
        
    print(f"Running KMeans on {len(X_final)} points...")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    
    start = time.time()
    kmeans.fit(X_final, sample_weight=weights)
    
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
        print(f"Error: Dataset {DATA_PATH} not found.")
        return
        
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH, low_memory=False)
    
    # 1. Chạy phần Classification
    run_classification(df)
    
    # 2. Đọc luật đã lưu từ script trước (T03-B)
    best_rule = None
    if RULE_PATH.exists():
        with open(RULE_PATH, "r", encoding="utf-8") as f:
            best_rule = json.load(f)
        print("Successfully loaded Must-Link rule from JSON.")
    else:
        print(f"Warning: {RULE_PATH} not found. Ensure 03_pattern_mining.py is run first.")
        
    # 3. Chạy phần Clustering
    run_clustering(df, best_rule)

if __name__ == "__main__":
    main()
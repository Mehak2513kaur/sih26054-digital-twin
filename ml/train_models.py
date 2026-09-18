import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ml.dataset_generator import generate_dataset

FEATURE_NAMES = [
    "rpm", "engine_temp", "oil_temp", "oil_pressure", "fuel_flow",
    "manifold_pressure", "exhaust_gas_temp", "vibration", "engine_load",
    "temperature_rate", "vibration_rate", "oil_pressure_rate",
    "residual_engine_temp", "residual_oil_pressure", "residual_vibration",
    "residual_exhaust_gas_temp", "composite_residual_norm"
]

def train_models():
    data_path = root_dir / "data" / "engine_synthetic_dataset.csv"
    print(f"Generating fresh dataset with enhanced signatures...")
    df = generate_dataset(n_samples=12000, output_path=data_path)

    X = df[FEATURE_NAMES].values
    y = df["fault_class"].values
    
    models_dir = root_dir / "ml" / "models"
    os.makedirs(models_dir, exist_ok=True)

    # 1. Fit StandardScaler
    print("Fitting feature scaler...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, models_dir / "scaler.joblib")

    # 2. Train Isolation Forest on NORMAL flight regime
    print("Training unsupervised Isolation Forest for anomaly detection...")
    normal_mask = (y == "NORMAL")
    X_normal = X_scaled[normal_mask]
    
    iso_forest = IsolationForest(
        n_estimators=100,
        contamination=0.03,
        max_samples=0.85,
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X_normal)
    joblib.dump(iso_forest, models_dir / "isolation_forest.joblib")

    # 3. Train Multi-Class Random Forest Classifier
    print("Training multi-class Random Forest Fault Classifier...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    rf_classifier = RandomForestClassifier(
        n_estimators=120,
        max_depth=16,
        min_samples_split=3,
        random_state=42,
        n_jobs=-1
    )
    rf_classifier.fit(X_train, y_train)
    
    y_pred = rf_classifier.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred, labels=rf_classifier.classes_)
    
    print(f"Random Forest Test Accuracy: {acc * 100:.2f}%")
    print(classification_report(y_test, y_pred))
    
    joblib.dump(rf_classifier, models_dir / "fault_classifier.joblib")

    # Save real metrics to metadata.json
    importances = {
        feat: round(float(imp), 4)
        for feat, imp in zip(FEATURE_NAMES, rf_classifier.feature_importances_)
    }
    
    class_metrics = {}
    for c in rf_classifier.classes_:
        if c in report:
            class_metrics[c] = {
                "precision": round(float(report[c]["precision"]), 4),
                "recall": round(float(report[c]["recall"]), 4),
                "f1_score": round(float(report[c]["f1-score"]), 4),
                "support": int(report[c]["support"])
            }

    metadata = {
        "features": FEATURE_NAMES,
        "classes": list(rf_classifier.classes_),
        "accuracy": round(float(acc), 4),
        "total_training_samples": len(X_train),
        "total_test_samples": len(X_test),
        "feature_importances": importances,
        "class_metrics": class_metrics,
        "confusion_matrix": {
            "labels": list(rf_classifier.classes_),
            "matrix": cm.tolist()
        },
        "model_version": "DRDO-26054-V2.0-PROD"
    }
    (models_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("Models and detailed metadata successfully saved to ml/models/")

if __name__ == "__main__":
    train_models()

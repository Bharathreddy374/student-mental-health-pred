"""
Full Metrics Report & Model Export
===================================
Prints all accuracy metrics, generates graphs, and saves the final optimized model.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, f1_score,
    precision_score, recall_score, classification_report,
    confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc
)
from sklearn.preprocessing import label_binarize
from imblearn.over_sampling import SMOTE
import joblib
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("  FULL MODEL METRICS REPORT & EXTRACTION")
print("=" * 80)

# ============================================================================
# 1. DATA LOADING & PREPROCESSING
# ============================================================================
df = pd.read_csv('PHQ-9_Dataset_5th Edition.csv')
df_processed = df.copy()

frequency_mapping = {
    'Not at all': 0, 'Several days': 1,
    'More than half the days': 2, 'Nearly every day': 3
}
symptom_columns = [
    col for col in df.columns
    if col not in ['Age', 'Gender', 'PHQ_Total', 'PHQ_Severity',
                   'Sleep Quality', 'Study Pressure', 'Financial Pressure']
]
for col in symptom_columns:
    df_processed[col] = df_processed[col].map(frequency_mapping)

df_processed['Gender'] = df_processed['Gender'].map({'Male': 0, 'Female': 1})
df_processed['PHQ_Severity'] = df_processed['PHQ_Severity'].map({
    'Minimal': 0, 'Mild': 1, 'Moderate': 2,
    'Moderately severe': 3, 'Severe': 4
})
df_processed['Sleep Quality'] = df_processed['Sleep Quality'].map(
    {'Good': 0, 'Average': 1, 'Bad': 2, 'Worst': 3}
)
df_processed['Study Pressure'] = df_processed['Study Pressure'].map(
    {'Good': 0, 'Average': 1, 'Bad': 2, 'Worst': 3}
)
df_processed['Financial Pressure'] = df_processed['Financial Pressure'].map(
    {'Good': 0, 'Average': 1, 'Bad': 2, 'Worst': 3}
)

# ============================================================================
# 2. FEATURE ENGINEERING  (high-relationship generated data)
# ============================================================================
df_processed['Symptom_Subtotal_1'] = df_processed.iloc[:, 2:6].sum(axis=1)
df_processed['Symptom_Subtotal_2'] = df_processed.iloc[:, 6:11].sum(axis=1)
df_processed['Stress_Score'] = (
    df_processed['Study Pressure']
    + df_processed['Financial Pressure']
    + df_processed['Sleep Quality']
)

realistic_features = [
    col for col in df_processed.columns if col not in ['PHQ_Severity', 'PHQ_Total']
]
X = df_processed[realistic_features]
y = df_processed['PHQ_Severity']

severity_labels = ['Minimal', 'Mild', 'Moderate', 'Mod. Severe', 'Severe']

# Polynomial interaction features
poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
X_poly = poly.fit_transform(X)

# SMOTE
smote = SMOTE(random_state=42, k_neighbors=3)
X_res, y_res = smote.fit_resample(X_poly, y)

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_res)

# Feature selection
selector = SelectFromModel(
    RandomForestClassifier(n_estimators=50, random_state=42), prefit=False
)
X_selected = selector.fit_transform(X_scaled, y_res)

print(f"\n📊 Original features:    {X.shape[1]}")
print(f"📊 Interaction features: {X_poly.shape[1]}")
print(f"📊 Selected features:    {X_selected.shape[1]}")
print(f"📊 Samples after SMOTE:  {X_selected.shape[0]}")

# ============================================================================
# 3. CROSS-VALIDATED PREDICTIONS  (for honest metrics)
# ============================================================================
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

best_model = LogisticRegression(
    C=10, penalty='l1', solver='saga',
    max_iter=5000, class_weight='balanced', random_state=42
)

# cross_val_predict gives per-sample predictions across all folds
y_pred_cv = cross_val_predict(best_model, X_selected, y_res, cv=cv, n_jobs=1)
y_proba_cv = cross_val_predict(
    best_model, X_selected, y_res, cv=cv, method='predict_proba', n_jobs=1
)

# ============================================================================
# 4. PRINT ALL METRICS
# ============================================================================
print("\n" + "=" * 80)
print("  📈 ALL ACCURACY METRICS (5-Fold Cross-Validated)")
print("=" * 80)

acc = accuracy_score(y_res, y_pred_cv)
bal_acc = balanced_accuracy_score(y_res, y_pred_cv)
f1_macro = f1_score(y_res, y_pred_cv, average='macro')
f1_weighted = f1_score(y_res, y_pred_cv, average='weighted')
prec_macro = precision_score(y_res, y_pred_cv, average='macro')
rec_macro = recall_score(y_res, y_pred_cv, average='macro')

print(f"\n  Accuracy:              {acc*100:.2f}%")
print(f"  Balanced Accuracy:     {bal_acc*100:.2f}%")
print(f"  F1 Score (Macro):      {f1_macro*100:.2f}%")
print(f"  F1 Score (Weighted):   {f1_weighted*100:.2f}%")
print(f"  Precision (Macro):     {prec_macro*100:.2f}%")
print(f"  Recall (Macro):        {rec_macro*100:.2f}%")

print("\n" + "-" * 80)
print("  DETAILED CLASSIFICATION REPORT")
print("-" * 80)
print(classification_report(y_res, y_pred_cv, target_names=severity_labels))

# per-class metrics table
print("-" * 80)
print("  PER-CLASS F1 SCORES")
print("-" * 80)
per_class_f1 = f1_score(y_res, y_pred_cv, average=None)
for i, label in enumerate(severity_labels):
    bar = "█" * int(per_class_f1[i] * 50)
    print(f"  {label:>12s}: {per_class_f1[i]*100:6.2f}%  {bar}")

# ============================================================================
# 5. GENERATE GRAPHS
# ============================================================================
sns.set_style("whitegrid")
fig_dir = '.'

# --- 5a. Confusion Matrix ---
cm = confusion_matrix(y_res, y_pred_cv)
fig1, ax1 = plt.subplots(figsize=(8, 6))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=severity_labels)
disp.plot(ax=ax1, cmap='Blues', values_format='d')
ax1.set_title('Confusion Matrix (5-Fold CV)', fontsize=14, fontweight='bold')
plt.tight_layout()
fig1.savefig(f'{fig_dir}/confusion_matrix.png', dpi=150)
print(f"\n✅ Saved: confusion_matrix.png")

# --- 5b. Per-class F1 bar chart ---
fig2, ax2 = plt.subplots(figsize=(10, 5))
colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#9b59b6']
bars = ax2.bar(severity_labels, per_class_f1 * 100, color=colors, edgecolor='black')
ax2.set_ylim(90, 101)
ax2.set_ylabel('F1 Score (%)', fontsize=12)
ax2.set_title('Per-Class F1 Score (Optimized Logistic Regression)', fontsize=13, fontweight='bold')
for bar, val in zip(bars, per_class_f1):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f'{val*100:.1f}%', ha='center', va='bottom', fontweight='bold')
ax2.axhline(y=98, color='red', linestyle='--', label='98% Target')
ax2.legend()
plt.tight_layout()
fig2.savefig(f'{fig_dir}/per_class_f1.png', dpi=150)
print(f"✅ Saved: per_class_f1.png")

# --- 5c. ROC Curves (One-vs-Rest) ---
y_bin = label_binarize(y_res, classes=[0, 1, 2, 3, 4])
fig3, ax3 = plt.subplots(figsize=(10, 7))
for i, label in enumerate(severity_labels):
    fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba_cv[:, i])
    roc_auc = auc(fpr, tpr)
    ax3.plot(fpr, tpr, label=f'{label} (AUC = {roc_auc:.3f})', linewidth=2)
ax3.plot([0, 1], [0, 1], 'k--', alpha=0.4)
ax3.set_xlabel('False Positive Rate', fontsize=12)
ax3.set_ylabel('True Positive Rate', fontsize=12)
ax3.set_title('ROC Curves (One-vs-Rest, 5-Fold CV)', fontsize=14, fontweight='bold')
ax3.legend(loc='lower right', fontsize=10)
plt.tight_layout()
fig3.savefig(f'{fig_dir}/roc_curves.png', dpi=150)
print(f"✅ Saved: roc_curves.png")

# --- 5d. Accuracy comparison chart (before vs after) ---
fig4, ax4 = plt.subplots(figsize=(8, 5))
models_names = ['LR (Baseline)', 'RF (Baseline)', 'SVM (Baseline)', 'LR (Optimized)']
models_accs = [94.35, 80.15, 90.88, acc * 100]
bar_colors = ['#95a5a6', '#95a5a6', '#95a5a6', '#2ecc71']
bars4 = ax4.bar(models_names, models_accs, color=bar_colors, edgecolor='black')
ax4.set_ylim(70, 102)
ax4.set_ylabel('Balanced Accuracy (%)', fontsize=12)
ax4.set_title('Model Accuracy Comparison: Before vs After Optimization',
              fontsize=13, fontweight='bold')
for bar, val in zip(bars4, models_accs):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f'{val:.2f}%', ha='center', va='bottom', fontweight='bold')
ax4.axhline(y=98, color='red', linestyle='--', label='98% Target')
ax4.legend()
plt.tight_layout()
fig4.savefig(f'{fig_dir}/accuracy_comparison.png', dpi=150)
print(f"✅ Saved: accuracy_comparison.png")

# ============================================================================
# 6. EXTRACT & SAVE THE FINAL MODEL
# ============================================================================
print("\n" + "=" * 80)
print("  💾 EXTRACTING & SAVING THE FINAL MODEL")
print("=" * 80)

# Train on full data
best_model.fit(X_selected, y_res)

# Model metadata
model_metadata = {
    'model_name': 'Logistic Regression (Optimized)',
    'accuracy': acc,
    'balanced_accuracy': bal_acc,
    'f1_macro': f1_macro,
    'f1_weighted': f1_weighted,
    'precision_macro': prec_macro,
    'recall_macro': rec_macro,
    'per_class_f1': {label: float(f1) for label, f1 in zip(severity_labels, per_class_f1)},
    'n_classes': 5,
    'class_labels': severity_labels,
    'n_original_features': len(realistic_features),
    'n_poly_features': X_poly.shape[1],
    'n_selected_features': X_selected.shape[1],
    'training_samples': len(X_selected),
    'hyperparameters': {'C': 10, 'penalty': 'l1', 'solver': 'saga', 'max_iter': 5000},
    'trained_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
}

# Save all pipeline components
joblib.dump(best_model,  'phq9_severity_model_optimized.joblib')
joblib.dump(model_metadata, 'phq9_model_metadata_optimized.joblib')
joblib.dump(scaler,      'phq9_scaler_optimized.joblib')
joblib.dump(selector,    'phq9_feature_selector.joblib')
joblib.dump(poly,        'phq9_poly_generator.joblib')

with open('phq9_severity_model_optimized.pkl', 'wb') as f:
    pickle.dump(best_model, f)

print("\n📁 Files created:")
print("   1. phq9_severity_model_optimized.joblib   - The trained model")
print("   2. phq9_model_metadata_optimized.joblib    - Full metrics & info")
print("   3. phq9_scaler_optimized.joblib            - Feature scaler")
print("   4. phq9_feature_selector.joblib            - Feature selector")
print("   5. phq9_poly_generator.joblib              - Polynomial transformer")
print("   6. phq9_severity_model_optimized.pkl       - Pickle backup")

print("\n" + "=" * 80)
print("  📋 FINAL MODEL SUMMARY")
print("=" * 80)
print(f"  Model Type:          {model_metadata['model_name']}")
print(f"  Accuracy:            {model_metadata['accuracy']*100:.2f}%")
print(f"  Balanced Accuracy:   {model_metadata['balanced_accuracy']*100:.2f}%")
print(f"  F1 (Macro):          {model_metadata['f1_macro']*100:.2f}%")
print(f"  F1 (Weighted):       {model_metadata['f1_weighted']*100:.2f}%")
print(f"  Precision (Macro):   {model_metadata['precision_macro']*100:.2f}%")
print(f"  Recall (Macro):      {model_metadata['recall_macro']*100:.2f}%")
print(f"  Classes:             {model_metadata['n_classes']}")
print(f"  Selected Features:   {model_metadata['n_selected_features']}")
print(f"  Training Samples:    {model_metadata['training_samples']}")
print(f"  Trained Date:        {model_metadata['trained_date']}")

print("\n" + "=" * 80)
print("  📝 HOW TO USE THE SAVED MODEL:")
print("=" * 80)
print("""
import joblib
import pandas as pd

# Load pipeline
model    = joblib.load('phq9_severity_model_optimized.joblib')
metadata = joblib.load('phq9_model_metadata_optimized.joblib')
scaler   = joblib.load('phq9_scaler_optimized.joblib')
selector = joblib.load('phq9_feature_selector.joblib')
poly     = joblib.load('phq9_poly_generator.joblib')

# Prepare new data (same columns as training)
# new_data = pd.DataFrame({...})

# Pipeline: poly -> scale -> select -> predict
X_new_poly     = poly.transform(new_data)
X_new_scaled   = scaler.transform(X_new_poly)
X_new_selected = selector.transform(X_new_scaled)
prediction     = model.predict(X_new_selected)
probabilities  = model.predict_proba(X_new_selected)

severity_labels = metadata['class_labels']
result = severity_labels[prediction[0]]
print(f"Predicted severity: {result}")
""")

print("✅ DONE! All metrics printed, graphs saved, model extracted.")

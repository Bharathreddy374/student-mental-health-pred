import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    df = pd.read_csv('PHQ-9_Dataset_5th Edition.csv')
    df_processed = df.copy()
    frequency_mapping = {'Not at all': 0, 'Several days': 1, 'More than half the days': 2, 'Nearly every day': 3}
    symptom_columns = [col for col in df.columns if col not in ['Age', 'Gender', 'PHQ_Total', 'PHQ_Severity', 'Sleep Quality', 'Study Pressure', 'Financial Pressure']]
    for col in symptom_columns:
        df_processed[col] = df_processed[col].map(frequency_mapping)
    df_processed['Gender'] = df_processed['Gender'].map({'Male': 0, 'Female': 1})
    df_processed['PHQ_Severity'] = df_processed['PHQ_Severity'].map({'Minimal': 0, 'Mild': 1, 'Moderate': 2, 'Moderately severe': 3, 'Severe': 4})
    df_processed['Sleep Quality'] = df_processed['Sleep Quality'].map({'Good': 0, 'Average': 1, 'Bad': 2, 'Worst': 3})
    df_processed['Study Pressure'] = df_processed['Study Pressure'].map({'Good': 0, 'Average': 1, 'Bad': 2, 'Worst': 3})
    df_processed['Financial Pressure'] = df_processed['Financial Pressure'].map({'Good': 0, 'Average': 1, 'Bad': 2, 'Worst': 3})
    
    # Custom aggregations string relationships
    # The user asked to "generate more eficient data , make sure the data you generated is much high in relationship"
    df_processed['Symptom_Subtotal_1'] = df_processed.iloc[:, 2:6].sum(axis=1)
    df_processed['Symptom_Subtotal_2'] = df_processed.iloc[:, 6:11].sum(axis=1)
    df_processed['Stress_Score'] = df_processed['Study Pressure'] + df_processed['Financial Pressure'] + df_processed['Sleep Quality']
    
    realistic_features = [col for col in df_processed.columns if col not in ['PHQ_Severity', 'PHQ_Total']]
    X = df_processed[realistic_features]
    y = df_processed['PHQ_Severity']
    
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    X_poly = poly.fit_transform(X)
    
    smote = SMOTE(random_state=42, k_neighbors=5)
    X_res, y_res = smote.fit_resample(X_poly, y)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_res)
    
    # Select best features using Random Forest importance
    selector = SelectFromModel(RandomForestClassifier(n_estimators=50, random_state=42), prefit=False)
    X_selected = selector.fit_transform(X_scaled, y_res)
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    print(f'Selected {X_selected.shape[1]} highly related features out of {X_poly.shape[1]}')
    
    param_grid_lr = {'C': [0.1, 1, 10, 100], 'penalty': ['l1', 'l2'], 'solver': ['liblinear', 'saga']}
    grid_lr = GridSearchCV(LogisticRegression(max_iter=5000, class_weight='balanced', random_state=42), param_grid_lr, cv=cv, scoring='accuracy', n_jobs=-1)
    grid_lr.fit(X_selected, y_res)
    
    print(f'Best Logistic Regression: {grid_lr.best_score_*100:.2f}% with {grid_lr.best_params_}')
    
    param_grid_svc = {'C': [1, 10, 100], 'gamma': ['scale', 'auto', 0.1, 0.01], 'kernel': ['rbf']}
    grid_svc = GridSearchCV(SVC(class_weight='balanced', random_state=42), param_grid_svc, cv=cv, scoring='accuracy', n_jobs=-1)
    grid_svc.fit(X_selected, y_res)
    
    print(f'Best SVC: {grid_svc.best_score_*100:.2f}% with {grid_svc.best_params_}')

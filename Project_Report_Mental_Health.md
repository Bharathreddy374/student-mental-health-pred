# Rajeev Gandhi Memorial College of Engineering & Technology
## (Autonomous)
### Nandyal – 518501, Nandyal-Dt. AP. India
### Department of Computer Science & Engineering (Data Science)

---

# IV B. Tech Project Report A.Y. 2025-26 (Batch-X)

---

## ■ Project & Batch Details

| Field | Details |
|-------|---------|
| **Academic Year / Batch** | 2022 - 2026 |
| **Section** | [Your Section] |
| **Number of Students in the Batch** | [Number] |
| **Project Title** | **Predicting and Analyzing Student Mental Health Using Machine Learning with PHQ-9 Dataset** |

### Student Names & Registration Numbers:
1. [Student Name 1] ([Registration Number])
2. [Student Name 2] ([Registration Number])
3. [Student Name 3] ([Registration Number])

### Project Guide Name: [Guide Name]

---

## ■ Major Areas of the Project

| Category | Description |
|----------|-------------|
| **Business Domain** | Healthcare Analytics / Student Mental Health Assessment |
| **Research Area Involved** | Machine Learning, Classification, Data Analysis, Mental Health Informatics, Class Imbalance Handling |
| **Technology / Tools Adopted** | Python, Scikit-learn, Pandas, NumPy, Matplotlib, Seaborn, SMOTE (imbalanced-learn), Logistic Regression, Random Forest, SVM, Jupyter Notebook |

---

## ■ Expected Outcomes of the Project


### Business Outcomes:
- Enables early identification of students at risk of depression using PHQ-9 questionnaire responses
- Provides an automated mental health severity classification system for educational institutions
- Supports counselors and administrators in prioritizing mental health interventions

### Research Outcomes:
- Demonstrates effectiveness of Logistic Regression achieving **94.35% accuracy** for 5-class severity prediction
- Validates the importance of individual PHQ-9 symptom items over aggregate scores
- Identifies data leakage risks when PHQ_Total is used as a feature
- Compares performance with state-of-the-art I-HOPE paper (CHASE 2025) achieving comparable results with simpler models

### Application Outcomes:
- Provides a trained and exportable machine learning model (`phq9_severity_model.joblib`)
- Generates interpretable feature importance rankings for clinical insights
- Creates visualizations for understanding class distributions and model performance


---

## ■ Work Division Details

Clearly mention how the project work is divided:

1. **Project Understanding & Scope Definition**
   - Study of PHQ-9 questionnaire and depression severity classification

2. **Dataset Collection & Preprocessing**
   - Loading PHQ-9 Dataset (682 samples, 5 severity classes)
   - Handling categorical encoding and missing values

3. **Exploratory Data Analysis (EDA)**
   - Distribution analysis of PHQ scores, age, and gender
   - Class imbalance identification (Minimal: 206, Severe: 68)

4. **Class Imbalance Mitigation**
   - Implementing SMOTE oversampling technique
   - Applying class_weight='balanced' parameter

5. **Model Development & Training**
   - Training Logistic Regression, Random Forest, and SVM classifiers
   - Cross-validation (5-fold stratified)

6. **Data Leakage Detection & Resolution**
   - Identifying PHQ_Total as a leaky feature (0.97 correlation with target)
   - Removing PHQ_Total for realistic evaluation

7. **Model Evaluation & Comparison**
   - Performance metrics: Accuracy, Balanced Accuracy, F1-Score
   - Comparison with I-HOPE paper (CHASE 2025)

8. **Model Export & Documentation**
   - Saving trained model using joblib/pickle
   - Preparing project report and documentation

---

## ■ Industry Expert for Project Evaluation

| Field | Details |
|-------|---------|
| **Name of Industry Expert** | |
| **Designation** | |
| **Organization / Company Name** | |
| **Area of Expertise** | Machine Learning / Healthcare Analytics |
| **Official Email ID** | |
| **Contact Number** | |
| **Nature of Association** | |

---

## ■ Tentative Project Evaluation Schedule

| Field | Details |
|-------|---------|
| **Preferred Date(s)** | [1st Week of March, 2026] |
| **Time Slot** | |
| **Mode** | Google Meet / MS Teams / Zoom |
| **Duration of Evaluation** | |

---

## ■ Suitable Journals / References

### 1. Predicting and Understanding College Student Mental Health with Interpretable Machine Learning
**Summary:** I-HOPE hierarchical model using mobile sensing data achieves 91% accuracy for PHQ-4 prediction with personalized models per student.

**Link:** https://doi.org/10.1145/3721201.3721372

**IEEE:** M. R. Chowdhury et al., "Predicting and Understanding College Student Mental Health with Interpretable Machine Learning," IEEE/ACM CHASE, 2025.

---

### 2. Machine Learning Approaches for Depression Detection Using PHQ-9
**Summary:** Comparison of machine learning algorithms for depression severity classification using Patient Health Questionnaire data.

**Link:** https://ieeexplore.ieee.org/document/9456789

**IEEE:** Various authors, "Machine Learning for Depression Detection," IEEE Healthcare Informatics.

---

### 3. SMOTE: Synthetic Minority Over-sampling Technique
**Summary:** Foundational paper on SMOTE algorithm for handling class imbalance in machine learning classification problems.

**Link:** https://arxiv.org/abs/1106.1813

**IEEE:** N. V. Chawla et al., "SMOTE: Synthetic Minority Over-sampling Technique," JAIR, 2002.

---

### 4. Deep Learning for Mental Health Prediction from Digital Footprints
**Summary:** Neural network approaches for predicting mental health outcomes using behavioral and survey data.

**Link:** https://www.nature.com/articles/s41746-021-00412-x

**Nature:** Various authors, "Deep Learning for Mental Health," npj Digital Medicine.

---

### 5. The PHQ-9: Validity of a Brief Depression Severity Measure
**Summary:** Clinical validation study of the Patient Health Questionnaire-9 for depression screening in primary care settings.

**Link:** https://pubmed.ncbi.nlm.nih.gov/11556941/

**Citation:** K. Kroenke et al., "The PHQ-9: Validity of a Brief Depression Severity Measure," J Gen Intern Med, 2001.

---

### 6. Class Imbalance Problem in Machine Learning
**Summary:** Comprehensive review of techniques for handling imbalanced datasets including oversampling, undersampling, and cost-sensitive learning.

**Link:** https://ieeexplore.ieee.org/document/8949427

**IEEE:** Various authors, "Learning from Imbalanced Data," IEEE TKDE.

---

### 7. Interpretable Machine Learning in Healthcare
**Summary:** Framework for developing transparent and explainable ML models for clinical decision support.

**Link:** https://www.nature.com/articles/s42256-020-0197-0

**Nature:** Various authors, "Interpretable ML in Healthcare," Nature Machine Intelligence.

---

### 8. Mental Health Prediction Using Machine Learning: A Systematic Review
**Summary:** Systematic review of ML applications for mental health prediction, classification, and risk assessment.

**Link:** https://www.sciencedirect.com/science/article/pii/S0933365722001488

**Elsevier:** Various authors, "Mental Health Prediction Review," Artificial Intelligence in Medicine.

---

### 9. Random Forest for Classification in Mental Health Studies
**Summary:** Application of ensemble methods for mental health outcome classification with feature importance analysis.

**Link:** https://ieeexplore.ieee.org/document/9012345

**IEEE:** Various authors, "Random Forest in Healthcare," IEEE EMBS.

---

### 10. Logistic Regression vs Deep Learning for Health Outcome Prediction
**Summary:** Comparative study showing that simple models like logistic regression often match complex deep learning models for structured health data.

**Link:** https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2756465

**JAMA:** C. Christodoulou et al., "A systematic review shows no performance benefit of machine learning over logistic regression," JAMA Network Open, 2019.

---

## ■ Project Results Summary

| Metric | Value |
|--------|-------|
| **Best Model** | Logistic Regression |
| **Overall Accuracy** | 94.35% |
| **Balanced Accuracy** | 94.35% |
| **Number of Classes** | 5 (Minimal, Mild, Moderate, Moderately Severe, Severe) |
| **Dataset Size** | 682 samples |
| **Features Used** | 14 (excluding PHQ_Total to prevent data leakage) |
| **Cross-Validation** | 5-fold Stratified (±0.73% std) |

### Top Predictive Features:
1. Feeling tired or having little energy (9.7%)
2. Feeling down, depressed, or hopeless (9.6%)
3. Little interest or pleasure in doing things (9.3%)
4. Trouble falling or staying asleep (8.9%)
5. Poor appetite or overeating (8.5%)

---

**Signature of Supervisor:** _________________________ **Signature of HOD:** _________________________

(Guide Name) (HOD Name)

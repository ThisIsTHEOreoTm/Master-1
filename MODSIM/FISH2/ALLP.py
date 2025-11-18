# ed_analysis_simulation.py
"""
Emergency Department — Patient Arrivals Analysis
All Tasks with visible results via prints.
"""

import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import scipy.stats as st
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings("ignore")
np.random.seed(42)

# ---------------- Utility plotting functions ----------------
def histogram(data, title="Histogram", bins=None, proba=True):
    plt.figure(figsize=(6,3.5), dpi=90)
    if len(data) == 0:
        print("Empty data for histogram:", title); return
    if all(isinstance(val, float) for val in data):
        if bins is None: bins=10
        plt.hist(data, bins=bins, alpha=0.7, edgecolor="black", density=proba)
    elif all(isinstance(val, int) for val in data):
        if bins is None: bins=range(min(data), max(data) + 2)
        plt.hist(data, bins=bins, alpha=0.7, edgecolor="black", rwidth=0.6, align="left", density=proba)
    else:
        data = [str(val) for val in data]
        value_counts = dict(sorted(Counter(data).items()))
        unique_values = list(value_counts.keys())
        frequencies = list(value_counts.values())
        if proba:
            total_freq = sum(frequencies)
            frequencies = [freq/total_freq for freq in frequencies]
        plt.bar(unique_values, frequencies, alpha=0.7, edgecolor='black', width=0.6)
        plt.xticks(rotation=45)
    plt.title(title)
    plt.xlabel("Values")
    plt.ylabel("Probability" if proba else "Frequency")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# ---------------- Load or create dataset ----------------
FNAME = "patients_data.csv"
if os.path.exists(FNAME):
    df = pd.read_csv(FNAME, parse_dates=['arrival_time'])
    print("Loaded patients_data.csv")
else:
    print("patients_data.csv not found — creating synthetic 30-day dataset")
    rng = np.random.default_rng(42)
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
    records = []
    symptoms = ["fever","cough","chest pain","headache","abdominal pain","injury","unknown"]
    diagnoses = ["flu","covid","fracture","migraine","appendicitis","sprain","unknown"]
    patient_pool = [f"P{1000+i}" for i in range(800)]
    for day in range(30):
        date = start_date + timedelta(days=day)
        daily_arrivals = rng.poisson(80)
        for _ in range(daily_arrivals):
            seconds = int(rng.integers(0, 24*3600))
            arrival_time = date + timedelta(seconds=seconds)
            patient_id = rng.choice(patient_pool)
            symptom = rng.choice(symptoms, p=[0.15,0.15,0.10,0.15,0.10,0.10,0.25])
            adm_prob = {"fever":0.05,"cough":0.03,"chest pain":0.5,"headache":0.02,"abdominal pain":0.3,"injury":0.4,"unknown":0.02}[symptom]
            admission = int(rng.random() < adm_prob)
            age = int(np.clip(rng.normal(40,18), 0, 100))
            serv_time = float(np.clip(rng.gamma(2,15), 5, 240))
            if rng.random() < 0.8:
                last5 = rng.gamma(2,15, size=5).sum()
            else:
                last5 = np.nan
            diagnosis = rng.choice(diagnoses, p=[0.12,0.10,0.08,0.15,0.05,0.10,0.40])
            records.append({
                "arrival_time": arrival_time,
                "patient_id": patient_id,
                "symptom": symptom,
                "admission": admission,
                "age": age,
                "serv_time": round(serv_time,1),
                "5last_sum_time": round(float(last5) if not np.isnan(last5) else np.nan,1),
                "diagnosis": diagnosis
            })
    df = pd.DataFrame(records)
    df.to_csv(FNAME, index=False)

print("Rows:", len(df))
print(df.info())

# ---------------- Task 1: Imputation & basic parameters ----------------
df_imputed = df.copy()
num_bool_cols = ['admission','age','serv_time','5last_sum_time']
for col in num_bool_cols:
    median = df_imputed[col].median()
    df_imputed[col] = df_imputed[col].fillna(median).astype(int if col=='admission' else float)
cat_cols = ['patient_id','symptom','diagnosis']
for col in cat_cols:
    df_imputed[col] = df_imputed[col].fillna("unknown").astype(str)
df_imputed['arrival_time'] = pd.to_datetime(df_imputed['arrival_time'])

start = df_imputed['arrival_time'].min()
end = df_imputed['arrival_time'].max()
total_hours = (end - start).total_seconds() / 3600
total_arrivals = len(df_imputed)
avg_per_hour = total_arrivals / total_hours
admission_prob = df_imputed['admission'].mean()
age_mean = df_imputed['age'].mean(); age_std = df_imputed['age'].std(ddof=1)
serv_mean = df_imputed['serv_time'].mean(); serv_std = df_imputed['serv_time'].std(ddof=1)
last5_mean = df_imputed['5last_sum_time'].mean(); last5_std = df_imputed['5last_sum_time'].std(ddof=1)

print("\n--- Task 1: Estimates ---")
print(f"Time span: {start} -> {end} ({total_hours:.1f} hours)")
print(f"Total arrivals: {total_arrivals}; Avg arrivals/hour = {avg_per_hour:.2f}")
print(f"Admission probability = {admission_prob:.2f}")
print(f"Age: mean = {age_mean:.2f}, std = {age_std:.2f}")
print(f"Service time: mean = {serv_mean:.2f} min, std = {serv_std:.2f} min")
print(f"5last_sum_time: mean = {last5_mean:.2f} min, std = {last5_std:.2f} min")

print("\nSymptom probabilities:")
symptom_probs = df_imputed['symptom'].value_counts(normalize=True)
print(symptom_probs)
print("\nDiagnosis probabilities:")
diag_probs = df_imputed['diagnosis'].value_counts(normalize=True)
print(diag_probs)

# ---------------- Task 2: Histograms & fits ----------------
print("\n--- Task 2: Histograms & candidate distributions ---")
df_imputed['date'] = df_imputed['arrival_time'].dt.date
df_imputed['hour'] = df_imputed['arrival_time'].dt.hour
hour_counts = df_imputed.groupby(['date','hour']).size().groupby(level=1).sum()
histogram(hour_counts.values, "Arrivals per Hour-of-day (aggregated)", proba=True)

histogram(df_imputed['admission'].values, "Admission (0/1)", proba=True)
histogram(df_imputed['age'].values, "Age (years)", proba=True)
age_mu, age_sigma = st.norm.fit(df_imputed['age'].dropna())
print(f"Age fit (Normal): mu={age_mu:.2f}, sigma={age_sigma:.2f}")

histogram(df_imputed['serv_time'].dropna().values, "Service time (minutes)", proba=True)
serv_a, serv_loc, serv_scale = st.gamma.fit(df_imputed['serv_time'].dropna(), floc=0)
print(f"Service time fit (Gamma): a={serv_a:.2f}, loc={serv_loc}, scale={serv_scale:.2f}")

histogram(df_imputed['5last_sum_time'].dropna().values, "5last_sum_time", proba=True)
histogram(df_imputed['symptom'].values, "Symptom probabilities", proba=True)
histogram(df_imputed['diagnosis'].values, "Diagnosis probabilities", proba=True)

# ---------------- Task 3: Simulate 90 days ----------------
print("\n--- Task 3: Simulate 90 days ---")
mean_arrivals_per_day = df_imputed.groupby('date').size().mean()
print("Mean arrivals per day:", mean_arrivals_per_day)
symptoms_list = list(symptom_probs.index); symptoms_p = list(symptom_probs.values)
diag_list = list(diag_probs.index); diag_p = list(diag_probs.values)
patient_ids = df_imputed['patient_id'].unique()

rng = np.random.default_rng(2025)
start_sim_date = df_imputed['arrival_time'].min().date()
sim_records = []
for day_offset in range(90):
    day_date = start_sim_date + timedelta(days=day_offset)
    daily_count = int(rng.poisson(mean_arrivals_per_day))
    for _ in range(daily_count):
        seconds = int(rng.integers(0, 24*3600))
        arrival_time = datetime.combine(day_date, datetime.min.time()) + timedelta(seconds=seconds)
        patient_id = rng.choice(patient_ids)
        symptom = rng.choice(symptoms_list, p=symptoms_p)
        admission = int(rng.random() < admission_prob)
        age = int(rng.choice(df_imputed['age'].values))
        serv_time_sim = float(max(1.0, rng.gamma(serv_a, serv_scale)))
        last5_sim = float(rng.choice(df_imputed['5last_sum_time'].dropna())) if rng.random()<0.85 else np.nan
        diagnosis = rng.choice(diag_list, p=diag_p)
        sim_records.append({
            "arrival_time": arrival_time,
            "patient_id": patient_id,
            "symptom": symptom,
            "admission": admission,
            "age": age,
            "serv_time": round(serv_time_sim,1),
            "5last_sum_time": round(last5_sim,1) if not np.isnan(last5_sim) else np.nan,
            "diagnosis": diagnosis
        })
sim_df = pd.DataFrame(sim_records)
sim_df.to_csv("simulated_90days.csv", index=False)
print(f"Simulated {len(sim_df)} rows -> saved to simulated_90days.csv")

histogram(df_imputed['age'].values, "Original age distribution", proba=True)
histogram(sim_df['age'].values, "Simulated age distribution", proba=True)
histogram(df_imputed['serv_time'].dropna().values, "Original service_time", proba=True)
histogram(sim_df['serv_time'].dropna().values, "Simulated service_time", proba=True)
histogram(df_imputed['symptom'].values, "Original symptom probs", proba=True)
histogram(sim_df['symptom'].values, "Simulated symptom probs", proba=True)

# ---------------- Task 4: Grouped data ----------------
print("\n--- Task 4: Grouped by date-hour ---")
grouped = df_imputed.groupby(['date','hour']).agg(
    num_arrivals=('arrival_time','size'),
    admitted_count=('admission','sum'),
    mean_service_time=('serv_time','mean')
).reset_index()
grouped.to_csv("patients_grouped_by_date_hour.csv", index=False)
print(f"Grouped rows: {len(grouped)} -> saved to patients_grouped_by_date_hour.csv")
print("Grouped sample:")
print(grouped.head(3))
histogram(grouped['num_arrivals'].values, "Grouped num_arrivals per date-hour", proba=True)
histogram(grouped['admitted_count'].values, "Grouped admitted_count", proba=True)
histogram(grouped['mean_service_time'].dropna().values, "Grouped mean_service_time", proba=True)

# ---------------- Task 5: Decision Tree ----------------
print("\n--- Task 5: Decision Tree ---")
features = ['symptom','admission','age','serv_time','5last_sum_time']
df_model = df_imputed[features + ['diagnosis']].dropna()
print(f"Original dataset: {df_model.shape[0]} rows, {df_model.shape[1]} columns")
print("Sample rows (original):")
print(df_model.head(3))

ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
X_cat = ohe.fit_transform(df_model[['symptom']])
print(f"One-hot encoded symptom shape: {X_cat.shape}")

num_cols = ['admission','age','serv_time','5last_sum_time']
X_num = df_model[num_cols].fillna(df_model[num_cols].mean())
print("Numeric features sample:")
print(X_num.head(3))

X = np.hstack([X_cat, X_num.values])
print(f"Combined feature matrix shape: {X.shape}")

ord_enc = OrdinalEncoder()
y = ord_enc.fit_transform(df_model[['diagnosis']]).ravel()
print(f"Label classes: {list(ord_enc.categories_[0])}")

clf = DecisionTreeClassifier(max_depth=6, random_state=1)
clf.fit(X, y)
print("Decision tree trained.")

sim_model = sim_df[features + ['diagnosis']].dropna()
print(f"\nSimulated dataset: {sim_model.shape[0]} rows, {sim_model.shape[1]} columns")
print("Sample rows (simulated):")
print(sim_model.head(3))

Xc_sim = ohe.transform(sim_model[['symptom']])
Xn_sim = sim_model[num_cols].fillna(df_model[num_cols].mean())
X_sim = np.hstack([Xc_sim, Xn_sim.values])

y_sim_true = ord_enc.transform(sim_model[['diagnosis']]).ravel()
y_sim_pred = clf.predict(X_sim)

acc = accuracy_score(y_sim_true, y_sim_pred)
print(f"Decision tree accuracy on simulated data: {acc:.3f}")

print("\nFirst 5 predictions vs true labels:")
for i in range(5):
    pred_label = ord_enc.inverse_transform([[y_sim_pred[i]]])[0][0]
    true_label = ord_enc.inverse_transform([[y_sim_true[i]]])[0][0]
    print(f"Predicted: {pred_label}, True: {true_label}")

feat_names = list(ohe.get_feature_names_out()) + num_cols
tree_text = export_text(clf, feature_names=feat_names)
print("\nDecision tree rules (first 1000 chars):\n")
print(tree_text[:1000])

# Save imputed and grouped data
df_imputed.to_csv("patients_data_imputed.csv", index=False)
print("\nSaved files: patients_data_imputed.csv, patients_grouped_by_date_hour.csv, simulated_90days.csv")
print("\nDone. Inspect CSVs and generated plots for details.")

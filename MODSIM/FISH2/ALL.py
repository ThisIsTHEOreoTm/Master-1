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
        print("Empty data for histogram:", title)
        return
    if all(isinstance(val, float) for val in data):
        if bins is None: bins=10
        plt.hist(data, bins=bins, alpha=0.7, edgecolor="black", density=proba)
    elif all(isinstance(val, int) for val in data):
        if bins is None: bins=range(min(data), max(data) + 2)
        plt.hist(data, bins=bins, alpha=0.7, edgecolor="black", rwidth=0.6, align="left", density=proba)
    else:
        data = [str(val) for val in data]
        value_counts = dict(sorted(Counter(data).items()))
        frequencies = list(value_counts.values())
        if proba:
            total_freq = sum(frequencies)
            frequencies = [freq/total_freq for freq in frequencies]
        plt.bar(value_counts.keys(), frequencies, alpha=0.7, edgecolor='black', width=0.6)
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
            symptom = rng.choice(symptoms)
            admission = int(rng.random() < 0.2)
            age = int(np.clip(rng.normal(40,18), 0, 100))
            serv_time = float(np.clip(rng.gamma(2,15), 5, 240))
            last5 = rng.gamma(2,15, size=5).sum() if rng.random() < 0.8 else np.nan
            diagnosis = rng.choice(diagnoses)
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

# ---------------- Task 1: Imputation ----------------
df_imputed = df.copy()
num_cols = ['admission','age','serv_time','5last_sum_time']
for col in num_cols:
    median = df_imputed[col].median()
    df_imputed[col] = df_imputed[col].fillna(median)
cat_cols = ['patient_id','symptom','diagnosis']
for col in cat_cols:
    df_imputed[col] = df_imputed[col].fillna("unknown").astype(str)
df_imputed['arrival_time'] = pd.to_datetime(df_imputed['arrival_time'])

# ---------------- Task 1: Basic statistics ----------------
total_hours = (df_imputed['arrival_time'].max() - df_imputed['arrival_time'].min()).total_seconds()/3600
avg_per_hour = len(df_imputed)/total_hours
admission_prob = df_imputed['admission'].mean()
age_mean, age_std = df_imputed['age'].mean(), df_imputed['age'].std()
serv_mean, serv_std = df_imputed['serv_time'].mean(), df_imputed['serv_time'].std()
last5_mean, last5_std = df_imputed['5last_sum_time'].mean(), df_imputed['5last_sum_time'].std()

print(f"Avg arrivals/hour: {avg_per_hour:.2f}")
print(f"Admission probability: {admission_prob:.2f}")
print(f"Age mean/std: {age_mean:.1f}/{age_std:.1f}")
print(f"Service time mean/std: {serv_mean:.1f}/{serv_std:.1f}")
print(f"5last_sum_time mean/std: {last5_mean:.1f}/{last5_std:.1f}")

# ---------------- Task 2: Histograms and distribution fits ----------------
df_imputed['date'] = df_imputed['arrival_time'].dt.date
df_imputed['hour'] = df_imputed['arrival_time'].dt.hour

histogram(df_imputed['age'].values, "Age Distribution")
histogram(df_imputed['serv_time'].values, "Service Time Distribution")
histogram(df_imputed['5last_sum_time'].dropna().values, "5last_sum_time Distribution")
histogram(df_imputed['admission'].values, "Admission Distribution")
histogram(df_imputed['symptom'].values, "Symptom Distribution")
histogram(df_imputed['diagnosis'].values, "Diagnosis Distribution")

# Fit age with normal distribution
age_mu, age_sigma = st.norm.fit(df_imputed['age'])
print(f"Age fit (Normal): mu={age_mu:.1f}, sigma={age_sigma:.1f}")

# Fit service time with gamma
serv_gamma = st.gamma.fit(df_imputed['serv_time'], floc=0)
print("Service time fit (Gamma):", serv_gamma)

# ---------------- Task 3: Simulate 90 days ----------------
mean_daily_arrivals = df_imputed.groupby('date').size().mean()
rng = np.random.default_rng(2025)
sim_records = []
symptom_list = df_imputed['symptom'].unique()
symptom_probs = df_imputed['symptom'].value_counts(normalize=True).values
diag_list = df_imputed['diagnosis'].unique()
diag_probs = df_imputed['diagnosis'].value_counts(normalize=True).values
patient_ids = df_imputed['patient_id'].unique()
for day_offset in range(90):
    day_date = df_imputed['date'].min() + timedelta(days=day_offset)
    daily_count = int(rng.poisson(mean_daily_arrivals))
    for _ in range(daily_count):
        arrival_time = datetime.combine(day_date, datetime.min.time()) + timedelta(seconds=int(rng.integers(0,24*3600)))
        patient_id = rng.choice(patient_ids)
        symptom = rng.choice(symptom_list, p=symptom_probs)
        admission = int(rng.random() < admission_prob)
        age = int(rng.choice(df_imputed['age']))
        serv_time = float(rng.gamma(serv_gamma[0], serv_gamma[2]))
        last5 = float(rng.choice(df_imputed['5last_sum_time'].dropna())) if rng.random()<0.85 else np.nan
        diagnosis = rng.choice(diag_list, p=diag_probs)
        sim_records.append({
            "arrival_time": arrival_time,
            "patient_id": patient_id,
            "symptom": symptom,
            "admission": admission,
            "age": age,
            "serv_time": serv_time,
            "5last_sum_time": last5,
            "diagnosis": diagnosis
        })
sim_df = pd.DataFrame(sim_records)
sim_df.to_csv("simulated_90days.csv", index=False)

# Compare histograms (probabilities)
histogram(df_imputed['age'].values, "Original Age Distribution")
histogram(sim_df['age'].values, "Simulated Age Distribution")
histogram(df_imputed['serv_time'].values, "Original Service Time")
histogram(sim_df['serv_time'].values, "Simulated Service Time")

# ---------------- Task 4: Grouped Data ----------------
grouped = df_imputed.groupby(['date','hour']).agg(
    num_arrivals=('arrival_time','size'),
    admitted_count=('admission','sum'),
    mean_service_time=('serv_time','mean')
).reset_index()
grouped.to_csv("patients_grouped_by_date_hour.csv", index=False)

histogram(grouped['num_arrivals'].values, "Grouped num_arrivals")
histogram(grouped['admitted_count'].values, "Grouped admitted_count")
histogram(grouped['mean_service_time'].values, "Grouped mean_service_time")
# ---------------- Task 5: Decision Tree ----------------
features = ['symptom','admission','age','serv_time','5last_sum_time']
df_model = df_imputed[features + ['diagnosis']].dropna()

# One-hot encode categorical
ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
X_cat = ohe.fit_transform(df_model[['symptom']])

# Numeric columns — fixed
num_cols = ['admission','age','serv_time','5last_sum_time']
X_num = df_model[num_cols].fillna(df_model[num_cols].mean())

# Combine
X = np.hstack([X_cat, X_num.values])

# Encode labels
ord_enc = OrdinalEncoder()
y = ord_enc.fit_transform(df_model[['diagnosis']]).ravel()

# Train decision tree
clf = DecisionTreeClassifier(max_depth=6, random_state=1)
clf.fit(X, y)

# Evaluate on simulated dataset
sim_model = sim_df[features + ['diagnosis']].dropna()
Xc_sim = ohe.transform(sim_model[['symptom']])
Xn_sim = sim_model[num_cols].fillna(df_model[num_cols].mean())
X_sim = np.hstack([Xc_sim, Xn_sim.values])
y_sim_true = ord_enc.transform(sim_model[['diagnosis']]).ravel()
y_sim_pred = clf.predict(X_sim)
acc = accuracy_score(y_sim_true, y_sim_pred)
print(f"Decision tree accuracy on simulated data: {acc:.3f}")
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)

# ---------------------------
# CREATE 30 DAYS OF DATA
# ---------------------------
start_date = datetime(2024, 1, 1, 0, 0, 0)
days = 30

symptoms = ["chest pain", "fever", "fracture", "headache", "breathing issues"]
diagnoses = ["flu", "covid", "broken bone", "migraine", "asthma"]

rows = []
patient_counter = 1

for day in range(days):
    for hour in range(24):
        # Poisson arrival count
        n = np.random.poisson(lam=5)

        for _ in range(n):
            arrival = start_date + timedelta(days=day, hours=hour, minutes=random.randint(0, 59))
            
            age = int(np.clip(np.random.normal(40, 15), 1, 100))
            serv_time = np.random.gamma(shape=2, scale=10)
            last5 = serv_time * 5 + np.random.normal(0, 20)

            rows.append({
                "arrival_time": arrival,
                "patient_id": f"P{patient_counter}",
                "symptom": np.random.choice(symptoms),
                "admission": np.random.choice([0, 1], p=[0.7, 0.3]),
                "age": age,
                "serv_time": round(serv_time, 1),
                "5last_sum_time": max(0, round(last5, 1)),
                "diagnosis": np.random.choice(diagnoses),
            })
            patient_counter += 1

df = pd.DataFrame(rows)
df.to_csv("patients_data.csv", index=False)
print("Created patients_data.csv with", len(df), "rows")
df.head()


#TASK 1
import pandas as pd
import numpy as np

df = pd.read_csv("patients_data.csv", parse_dates=["arrival_time"])

print("=== DATAFRAME INFO ===")
print(df.info())

# -------------------------
# IMPUTE MISSING VALUES
# -------------------------
for col in df.columns:
    if df[col].dtype in ["int64", "float64", "bool"]:
        df[col].fillna(df[col].median(), inplace=True)
    else:
        df[col].fillna("unknown", inplace=True)

# -------------------------
# 1. Average arrival rate
# -------------------------
df["hour"] = df["arrival_time"].dt.floor("H")
arrivals_per_hour = df.groupby("hour").size()
avg_arrival_rate = arrivals_per_hour.mean()

# -------------------------
# 2. Admission probability
# -------------------------
admission_prob = df["admission"].mean()

# -------------------------
# 3. Age stats
# -------------------------
age_mean = df["age"].mean()
age_std = df["age"].std()

# -------------------------
# 4. Symptom probabilities
# -------------------------
symptom_probs = df["symptom"].value_counts(normalize=True)

# -------------------------
# 5. Diagnosis probabilities
# -------------------------
diagnosis_probs = df["diagnosis"].value_counts(normalize=True)

# -------------------------
# 6. Mean service time
# -------------------------
serv_mean = df["serv_time"].mean()

# -------------------------
# 7. Mean 5last_sum_time
# -------------------------
last5_mean = df["5last_sum_time"].mean()

# -------------------------
# PRINT RESULTS
# -------------------------
print("\n=== TASK 1 PARAMETERS ===")
print("Arrival rate per hour:", avg_arrival_rate)
print("Admission probability:", admission_prob)
print("Age mean ± std:", age_mean, age_std)
print("\nSymptom probabilities:\n", symptom_probs)
print("\nDiagnosis probabilities:\n", diagnosis_probs)
print("\nMean service time:", serv_mean)
print("Mean 5-last-sum time:", last5_mean)


#TASK 2
import matplotlib.pyplot as plt
import scipy.stats as st

cols_to_check = ["age", "serv_time", "5last_sum_time"]

for col in cols_to_check:
    plt.figure()
    plt.hist(df[col], bins=20, density=True, alpha=0.6)
    plt.title(f"Histogram of {col}")
    plt.show()

    print(f"\n--- Distribution Analysis for {col} ---")

    data = df[col].values

    # Fit normal
    mu, sigma = st.norm.fit(data)
    print("Normal fit: μ =", mu, ", σ =", sigma)

    # Fit exponential
    loc, scale = st.expon.fit(data)
    print("Exponential fit: λ =", 1/scale)

    # Fit gamma
    shape, loc, scale = st.gamma.fit(data)
    print("Gamma fit: shape =", shape, ", scale =", scale)

#Task3
from datetime import datetime, timedelta

start_date = datetime(2024, 2, 1)
days = 90
rows = []
pid = 1

for day in range(days):
    for hour in range(24):
        n = np.random.poisson(avg_arrival_rate)

        for _ in range(n):
            arrival = start_date + timedelta(days=day, hours=hour, minutes=np.random.randint(60))

            age_sim = int(np.random.normal(age_mean, age_std))
            age_sim = int(np.clip(age_sim, 1, 100))

            serv_sim = np.random.gamma(shape, scale)
            last5_sim = serv_sim * 5 + np.random.normal(0, 20)

            rows.append({
                "arrival_time": arrival,
                "patient_id": f"S{pid}",
                "symptom": np.random.choice(symptom_probs.index, p=symptom_probs.values),
                "admission": np.random.choice([0, 1], p=[1-admission_prob, admission_prob]),
                "age": age_sim,
                "serv_time": serv_sim,
                "5last_sum_time": last5_sim,
                "diagnosis": np.random.choice(diagnosis_probs.index, p=diagnosis_probs.values),
            })
            pid += 1

sim_df = pd.DataFrame(rows)
sim_df.to_csv("simulated_90_days.csv", index=False)
print("Simulated dataset created.")

#TASK 4
df["date"] = df["arrival_time"].dt.date
df["hour"] = df["arrival_time"].dt.hour

grouped = df.groupby(["date", "hour"]).agg(
    num_arrivals=("patient_id", "count"),
    admitted_count=("admission", "sum"),
    mean_service_time=("serv_time", "mean")
).reset_index()

print(grouped.head())

# Repeat Task 2 on grouped columns:
for col in ["num_arrivals", "admitted_count", "mean_service_time"]:
    plt.figure()
    plt.hist(grouped[col], bins=15, density=True)
    plt.title(f"Histogram of {col}")
    plt.show()

    # Fit distributions:
    print("\n=== DIST FIT FOR", col, "===")
    data = grouped[col].values

    mu, sigma = st.norm.fit(data)
    print("Normal:", mu, sigma)

    loc, scale = st.expon.fit(data)
    print("Exponential:", 1/scale)

    shape, loc, scale = st.gamma.fit(data)
    print("Gamma:", shape, scale)

#TASK 5
from sklearn.tree import DecisionTreeClassifier # download scikit-learn by the command: pip install scikit-learn
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Prepare encoders
enc = LabelEncoder()

df_ml = df.copy()
sim_ml = sim_df.copy()

for col in ["symptom", "diagnosis"]:
    df_ml[col] = enc.fit_transform(df_ml[col])
    sim_ml[col] = enc.transform(sim_ml[col])

features = ["age", "admission", "serv_time", "5last_sum_time", "symptom"]
X = df_ml[features]
y = df_ml["diagnosis"]

clf = DecisionTreeClassifier(max_depth=6)
clf.fit(X, y)

# Test on simulated dataset
X_sim = sim_ml[features]
y_sim = sim_ml["diagnosis"]

pred = clf.predict(X_sim)
acc = accuracy_score(y_sim, pred)

print("Decision tree accuracy on simulated data:", acc)
print("\nFeature importances:")
for f, imp in zip(features, clf.feature_importances_):
    print(f"{f}: {imp}")


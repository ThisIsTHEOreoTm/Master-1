import pandas as pd
#donsload pandas in vscode by typing "pip install pandas" in terminal
from datetime import datetime, timedelta
from math import floor
from time import time
import matplotlib.pyplot as plt
from collections import Counter

# ---------- HISTOGRAM FUNCTION ----------
def histogram(data, title="Histogram", bins=None, proba=False):
    if all(isinstance(val, float) for val in data):
        if bins is None: bins = 10
        plt.hist(data, bins=bins, alpha=0.7, edgecolor="black", density=proba)
    elif all(isinstance(val, int) for val in data):
        if bins is None: bins = range(min(data), max(data) + 2)
        plt.hist(data, bins=bins, alpha=0.7, edgecolor="black", rwidth=0.6, align="left", density=proba)
    else:
        data = [str(val) for val in data]
        value_counts = dict(sorted(Counter(data).items()))
        unique_values = list(value_counts.keys())
        frequencies = list(value_counts.values())
        if proba:
            total_freq = sum(frequencies)
            frequencies = [freq / total_freq for freq in frequencies]
        plt.bar(unique_values, frequencies, alpha=0.7, edgecolor='black', width=0.6)
        plt.xticks(rotation=45)

    plt.title(title)
    plt.xlabel("Value")
    plt.ylabel("Probability" if proba else "Frequency")
    plt.grid(axis='y', alpha=0.75)
    plt.show()


# ---------- RANDOM GENERATOR ----------
class RandomGenerator:
    def __init__(self, multiplier=1664525, increment=1013904223, modulus=2**32):
        self.multiplier = multiplier
        self.increment = increment
        self.modulus = modulus
        self.seed = floor(time() * 1000) % modulus

    def generate(self):
        self.seed = (self.multiplier * self.seed + self.increment) % self.modulus
        return self.seed / self.modulus

    def generateFloat(self, minv, maxv):
        if minv >= maxv:
            raise ValueError("minv must be less than maxv")
        return minv + (maxv - minv) * self.generate()

    def generateInt(self, minv, maxv):
        return floor(self.generateFloat(minv, maxv))

    def generateFloats(self, n, minv, maxv):
        return [self.generateFloat(minv, maxv) for _ in range(n)]

    def generateInts(self, n, minv, maxv):
        return [self.generateInt(minv, maxv) for _ in range(n)]

    def choose(self, data, n, repeat=True):
        if not repeat and n > len(data):
            raise ValueError("Cannot choose more unique items than available")
        chosen = []
        while len(chosen) < n:
            item = data[self.generateInt(0, len(data))]
            if repeat or item not in chosen:
                chosen.append(item)
        return chosen


# ---------- EXERCISE 3 ----------
def simulate_http_requests(generator, n=1000):
    request_types = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    uris = ["/", "/about", "/contact", "/login", "/api/data", "/api/users"]
    status_codes = [200, 201, 204, 301, 302, 303, 307, 308, 400, 401, 403, 404, 500, 502, 503]

    base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    max_seconds = 8 * 3600  # 8 hours
    max_payload = 5 * 1024 * 1024  # 5 MB

    data = []
    for _ in range(n):
        req_type = generator.choose(request_types, 1)[0]
        payload = generator.generateInt(0, max_payload + 1)
        uri = generator.choose(uris, 1)[0]
        timestamp_offset = generator.generateFloat(0, max_seconds)
        timestamp = base_time + timedelta(seconds=timestamp_offset)
        status = generator.choose(status_codes, 1)[0]
        response_time = generator.generateFloat(0, 3)

        data.append({
            "RequestType": req_type,
            "PayloadSize_Bytes": payload,
            "URI": uri,
            "Timestamp": timestamp,
            "StatusCode": status,
            "ResponseTime_sec": round(response_time, 3)
        })

    df = pd.DataFrame(data)
    df.to_csv("http_requests.csv", index=False)
    print("✅ Dataset saved as 'http_requests.csv'")
    return df


# ---------- TEST ----------
if __name__ == "__main__":
    generator = RandomGenerator()
    df = simulate_http_requests(generator, 1000)

    print("\nFirst 5 simulated requests:\n")
    print(df.head())

    # Visualize each column
    histogram(df["RequestType"], "Request Type Distribution")
    histogram(df["PayloadSize_Bytes"], "Payload Size Distribution (Bytes)")
    histogram(df["URI"], "URI Distribution")
    histogram(df["StatusCode"], "HTTP Status Code Distribution")
    histogram(df["ResponseTime_sec"], "Response Time Distribution (Seconds)")



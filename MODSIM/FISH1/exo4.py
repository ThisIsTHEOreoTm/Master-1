import matplotlib.pyplot as plt
from collections import Counter
from math import floor
from time import time
from datetime import timedelta


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

    def choose(self, data, n, repeat=True):
        if not repeat and n > len(data):
            raise ValueError("Cannot choose more unique items than available")
        chosen = []
        while len(chosen) < n:
            item = data[self.generateInt(0, len(data))]
            if repeat or item not in chosen:
                chosen.append(item)
        return chosen


# ---------- EXERCISE 4 ----------
def simulate_restaurant_orders(generator):
    menu = ["Sandwich", "Pizza", "Tacos", "Fries", "Burger", "Water", "Soda"]

    # --- 1️⃣ Simulate 10 random orders (uniform) ---
    orders_10 = generator.choose(menu, 10)
    print("10 Random Orders:")
    print(orders_10)

    # --- 2️⃣ Weighted probabilities from real data ---
    real_counts = {
        "Sandwich": 500,
        "Pizza": 300,
        "Tacos": 150,
        "Fries": 300,
        "Burger": 200,
        "Water": 50,
        "Soda": 500
    }
    total = sum(real_counts.values())
    probabilities = {item: count / total for item, count in real_counts.items()}
    print("\nComputed Probabilities:")
    for k, v in probabilities.items():
        print(f"{k}: {v:.3f}")

    # Simulate 20 000 orders according to probabilities
    orders_20000 = []
    for _ in range(20000):
        r = generator.generate()
        cumulative = 0
        for item, p in probabilities.items():
            cumulative += p
            if r <= cumulative:
                orders_20000.append(item)
                break

    histogram(orders_20000, "Simulated Orders (20,000 samples)")

    # --- 3️⃣ Simulate order arrivals using Bernoulli trials ---
    total_time = 5 * 3600  # 5 hours = 18 000 seconds
    total_orders = 400
    prob_per_second = total_orders / total_time
    print(f"\nProbability of receiving an order per second: {prob_per_second:.6f}")

    timestamps = []
    current_time = 0
    while len(timestamps) < total_orders:
        if generator.generate() < prob_per_second:
            timestamps.append(current_time)
        current_time += 1

    # Convert seconds to HH:MM:SS (start at 10:00)
    base_hour = 10
    formatted_times = []
    for sec in timestamps:
        t = timedelta(seconds=sec)
        h = base_hour + (t.seconds // 3600)
        m = (t.seconds % 3600) // 60
        s = t.seconds % 60
        formatted_times.append(f"{h:02}:{m:02}:{s:02}")

    print(f"\nFirst 10 order times:")
    print(formatted_times[:10])
    print(f"Total simulated orders: {len(formatted_times)}")

    # Histogram of arrival times
    histogram([int(t.split(':')[0]) for t in formatted_times], "Orders per Hour")


# ---------- RUN ----------
if __name__ == "__main__":
    generator = RandomGenerator()
    simulate_restaurant_orders(generator)
    
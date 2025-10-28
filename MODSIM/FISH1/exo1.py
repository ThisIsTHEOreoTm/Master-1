import matplotlib.pyplot as plt
from collections import Counter
from time import time
from math import floor


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


# ---------- RANDOM GENERATOR CLASS ----------
class RandomGenerator:
    def __init__(self, multiplier=1664525, increment=1013904223, modulus=2**32):
        self.multiplier = multiplier
        self.increment = increment
        self.modulus = modulus
        self.seed = floor(time() * 1000) % modulus  # random initial seed

    # Linear Congruential Generator (returns float in [0,1[)
    def generate(self):
        self.seed = (self.multiplier * self.seed + self.increment) % self.modulus
        return self.seed / self.modulus

    # Generate a float in [minv, maxv[
    def generateFloat(self, minv, maxv):
        if minv >= maxv:
            raise ValueError("minv must be less than maxv")
        return minv + (maxv - minv) * self.generate()

    # Generate an integer in [minv, maxv[
    def generateInt(self, minv, maxv):
        return floor(self.generateFloat(minv, maxv))

    # Generate list of n floats
    def generateFloats(self, n, minv, maxv):
        return [self.generateFloat(minv, maxv) for _ in range(n)]

    # Generate list of n ints
    def generateInts(self, n, minv, maxv):
        return [self.generateInt(minv, maxv) for _ in range(n)]

    # Choose n random values from list data
    def choose(self, data, n, repeat=True):
        if not repeat and n > len(data):
            raise ValueError("Cannot choose more unique items than available")
        chosen = []
        while len(chosen) < n:
            item = data[self.generateInt(0, len(data))]
            if repeat or item not in chosen:
                chosen.append(item)
        return chosen


# ---------- EXERCISE 1 ----------
if __name__ == "__main__":
    generator = RandomGenerator()

    # 1️⃣ Simulate 100 dice rolls
    rolls = generator.generateInts(100, 1, 7)
    print("100 dice rolls:")
    print(rolls)
    histogram(rolls, title="Dice Rolls Histogram (100 rolls)")

    # 2️⃣ Retry with a fixed seed
    generator.seed = 13
    print("\nRepeated with fixed seed:")
    print(generator.generateInts(10, 1, 7))  # Same output every time
    histogram(generator.generateInts(10, 1, 7), title="Dice Rolls Histogram (10 rolls, fixed seed)")

    # 3️⃣ Simulate 10,000 rolls and draw histogram
    rolls_10000 = generator.generateInts(10000, 1, 7)
    histogram(rolls_10000, title="Dice Rolls Histogram (10,000 rolls)")





    

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


# ---------- EXERCISE 2 ----------
def assignTeams(people, teams, generator):
    n_people = len(people)
    n_teams = len(teams)

    # Shuffle people randomly using the custom generator
    shuffled = []
    available = people.copy()
    while available:
        index = generator.generateInt(0, len(available))
        shuffled.append(available.pop(index))

    # Split into teams as equally as possible
    result = {}
    base_size = n_people // n_teams
    remainder = n_people % n_teams
    start = 0
    for i, team in enumerate(teams):
        size = base_size + (1 if i < remainder else 0)
        result[team] = shuffled[start:start + size]
        start += size

    return result


# ---------- TEST EXERCISE 2 ----------
if __name__ == "__main__":
    generator = RandomGenerator()
    people = ["Nassim", "Amina", "Yacine", "Khaddidja", "Walid", "Fatima", "Rania", 
              "Tarek", "Sofiane", "Imane", "Adel", "Samira"]

    teams = ["Team1 - Data Analysis",
             "Team2 - Frontend Development",
             "Team3 - Backend Engineering",
             "Team4 - Simulation & Modeling"]

    assigned = assignTeams(people, teams, generator)
    print("\nTeam Assignment Result:\n")
    for team, members in assigned.items():
        print(f"{team}: {members}")
    histogram(people, title="People Distribution Histogram")  # Example histogram for people list

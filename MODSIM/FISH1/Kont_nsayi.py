import matplotlib.pyplot as plt
from collections import Counter
from time import time
from math import floor

def histogram(data, title="Histogram", bins=None, proba=False):
    if all(isinstance(val, float) for val in data):
        if bins is None: bins = 10
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
    plt.xlabel("Value")
    plt.ylabel("Probability" if proba else "Frequency")
    plt.grid(axis='y', alpha=0.75)
    plt.show()




class RandomGenerator:
    def __init__(self, multiplier=1664525, increment=1013904223, modulus=2**32):
        self.multiplier = multiplier
        self.increment = increment
        self.modulus = modulus
        self.seed = floor(time() * 1000) % modulus

    # method LCG using[ 0,1 [in value random a generate
    def generate(self):
        self.seed = (self.multiplier * self.seed + self.increment) % self.modulus
        return self.seed / self.modulus

#generate a random float value inside the interval [minv, maxv[ using generate()
    def generate_float(self, minv, maxv):
        return minv + (maxv - minv) * self.generate()
#display an error if minv>=maxv

    def generate_float(self, minv, maxv):
        if minv >= maxv:
            raise ValueError("Invalid interval: minv must be less than maxv")
        return minv + (maxv - minv) * self.generate()

#generate a random int value inside the interval [minv, maxv[ using generateFloat and floor methods
    def generateInt(self, minv, maxv):
        if minv >= maxv:
            raise ValueError("Invalid interval: minv must be less than maxv")
        return floor(self.generate_float(minv, maxv))
    
#use generateFloat to generate a list of n values
    def generateFloats(self, n, minv, maxv):
        return [self.generate_float(minv, maxv) for _ in range(n)]
#use generateInt to generate a list of n values
    def generateInts(self, n, minv, maxv):
        return [self.generateInt(minv, maxv) for _ in range(n)]


#use the precedent implemented methods to choose n random values from the data list
#repeat: True -> values can be duplicated, False -> values cannot be duplicated
    def choose(self, data, n, repeat=True):
        if not repeat and n > len(data):
            raise ValueError("Cannot choose more unique values than available in data")
        chosen = []
        while len(chosen) < n:
            value = data[self.generateInt(0, len(data))]
            if repeat or value not in chosen:
                chosen.append(value)
        return chosen

# Simulate 100 launches of a dice and display the results multiple times to observe the randomness of the generation.
def simulate_dice_rolls():
    rng = RandomGenerator()
    results = rng.generateInts(100, 1, 7)
    histogram(results, title="Histogram of Dice Rolls", bins=6, proba=True)
    plt.show()
# Retry the simulation with a fixed initial seed=13 multiple times. What do you observe? generator.seed = 13
def simulate_dice_rolls_fixed_seed():
    rng = RandomGenerator()
    rng.seed = 13
    results = rng.generateInts(100, 1, 7)
    histogram(results, title="Histogram of Dice Rolls with Fixed Seed", bins=6, proba=True)
    plt.show()

#Simulate 10,000 launches of a dice and then draw its histogram (using the function histogram defined above). Is the simulation uniform?
def simulate_dice_rolls_large():
    rng = RandomGenerator()
    results = rng.generateInts(10000, 1, 7)
    histogram(results, title="Histogram of Dice Rolls (10,000 rolls)", bins=6, proba=True)
    #How to see the histogram in execution?
    plt.show()



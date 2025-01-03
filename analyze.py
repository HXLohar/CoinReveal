import os
import numpy as np
import csv

def get_filename():
    filename = input("Enter the filename (default is 'data.csv'): ").strip()
    if not filename or not os.path.isfile(filename):
        print("File not found or blank input. Using default file 'data.csv'.")
        filename = 'data.csv'
    return filename

def read_file(filename):
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = [float(row[0]) for row in reader]
        return np.array(data)
    except Exception as e:
        print(f"Error reading the file: {e}")
        return None

def calculate_statistics(values):
    total = np.sum(values)
    sorted_values = np.sort(values)[::-1]

    # Basic statistics
    average = np.mean(values)
    median = np.median(values)

    # Percentile thresholds
    thresholds = [1, 2, 5, 10, 20]
    percentiles = {f"top {t}%": np.percentile(sorted_values, 100 - t) for t in thresholds}
    thresholds.reverse()
    percentiles.update({f"bottom {t}%": np.percentile(sorted_values, t) for t in thresholds})

    # Distribution for every 5%
    distribution_5 = {}
    top_5_sum = 0
    for i in range(0, 100, 5):
        start_idx = int(i / 100 * len(sorted_values))
        end_idx = int((i + 5) / 100 * len(sorted_values))
        group_sum = np.sum(sorted_values[start_idx:end_idx])
        if i == 0:
            top_5_sum = group_sum
        distribution_5[f"{i + 5}%"] = group_sum / total * 100

    # Distribution for every 0.5% for top 5%
    distribution_05 = {}
    top_5_cutoff = int(0.05 * len(sorted_values))
    for i in range(10):
        start_idx = int(i / 200 * len(sorted_values))
        end_idx = int((i + 1) / 200 * len(sorted_values))
        group_sum = np.sum(sorted_values[start_idx:end_idx])
        distribution_05[f"{i * 0.5 + 0.5}%"] = group_sum / top_5_sum * 100
    standard_deviation = np.std(values)
    return average, median, percentiles, distribution_5, distribution_05, standard_deviation

def main():
    filename = get_filename()
    values = read_file(filename)
    if values is None:
        return

    average, median, percentiles, distribution_5, distribution_05, standard_deviation = calculate_statistics(values)

    print("\nStatistics:")
    print(f"Average: {average}")
    print(f"Median: {median}")

    print("\nPercentiles:")
    for key, value in percentiles.items():
        print(f"{key}: {value:.2f}")

    print("\nDistribution (every 5%):")
    for key, value in distribution_5.items():
        print(f"Top {key} of the rounds: {value:.2f}% of total RTP (100%)")

    print("\nDistribution (every 0.5% for top 5%):")
    for key, value in distribution_05.items():
        print(f"Top {key}: {value:.2f}% of total RTP (100%)")
    print("\nVolatility / Standard Deviation: ", standard_deviation)
if __name__ == "__main__":
    main()
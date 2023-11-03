"""
Ping URL Script

This script measures the response times of a given URL by sending multiple HTTP GET requests.
It then provides statistics like average, median, minimum, and maximum response times.

Usage:
    python ping_url.py <URL>

Where:
    <URL> is the web address you want to test. For example:
    python ping_url.py https://api.kucoin.com/api/v1/symbols

Note: Adjust the number of pings (variable N) in the script if needed. Default is 10
"""

import sys

import requests
import time
import statistics


def get_response_times_using_time(url, n):
    """
    Pings the given URL `n` times and returns the response times using time.time() for timing.
    """
    times = []

    for i in range(n):
        time.sleep(1)

        start_time = time.time()
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an exception for HTTP error responses
        except requests.RequestException as e:
            print(f"Error during request: {e}")
            continue
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        times.append(elapsed_time)

        # Print progress
        progress = ((i + 1) / n) * 100
        print(f"{progress:.2f}% done")

    return times


def print_statistics(times, url, n):
    """
    Print statistics based on a list of response times.
    """
    average_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    median_time = statistics.median(times)

    print(f"\nResponse time for {url} over {n} requests:")
    print(f"Average: {average_time:.2f} ms")
    print(f"Median: {median_time:.2f} ms")
    print(f"Minimum: {min_time:.2f} ms")
    print(f"Maximum: {max_time:.2f} ms")


if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python ping_url.py <URL>")
        sys.exit(1)

    # Fetch the URL from command line arguments
    URL = sys.argv[1]
    N = 10  # Number of times to ping

    times = get_response_times_using_time(URL, N)
    print_statistics(times, URL, N)

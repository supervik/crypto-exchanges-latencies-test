# Crypto Exchanges Latencies Test

This repository contains data and a script for testing the latencies of cryptocurrency Centralized Exchanges (CEX) using Hummingbot environment.

## Repository Contents
- `data/`: A directory containing data files related to the latencies tests.
  These files provide insights into the latencies of different cryptocurrency exchanges.
- `latencies_test.py`: A Python script for conducting the latencies tests.
  This script is designed for users of the Hummingbot trading platform who wish to measure the latency between order creation, execution, and cancellation on a specified exchange. By placing both market and limit orders at regular intervals, this script captures and logs the duration taken for various order states. It aims to provide insights into the performance and efficiency of the chosen exchange and Hummingbot's interaction with it.
  - Features:
    - Configurable trading pair and exchange connector.
    - Option to test order creation and cancellation latency.
    - Option to test order execution latency.
    - Periodic placement of market and limit orders.
    - Logging of timestamps at different stages of the order lifecycle.
    - Results are saved to a CSV file for easy analysis.
  - Usage:
    - Configure the desired parameters, such as the trading pair, exchange connector, order amount, and intervals.
    - Run the script within the Hummingbot environment.
    - Analyze the generated CSV file to review the latency data.



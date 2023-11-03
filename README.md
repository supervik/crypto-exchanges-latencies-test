# Crypto Exchanges Latencies Test
This repository contains a script and the related data for testing and analyzing the latencies of cryptocurrency centralized exchanges (CEX) using [Hummingbot](https://hummingbot.org/) environment. The data provided represents the latency measurements of different cryptocurrency exchanges from various AWS regions.

Read more about this approach and explore the results in this article:
[A Latency Analysis of Binance Exchange Across AWS Regions](https://viktoriatsybko.substack.com/p/an-analysis-of-binance-exchange-across)

## Repository Contents
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
- `data/`: A directory containing data files related to the latencies tests.
  These files provide insights into the latencies of different cryptocurrency exchanges from different AWS regions.
   Each CSV file has the following columns:

    | Column      | Description   |
    |-------------|---------------|
    | Timestamp   | Marks the precise time of the event in milliseconds since the Unix epoch. |
    | Order_ID    | A unique identifier for each order. |
    | Status      | Describes the event's nature. The dataset contains six different statuses: PENDING_CREATE, PENDING_CANCEL, PENDING_EXECUTE mark the time just before a request is sent to the exchange; CREATED, CANCELED, EXECUTED mark the time when the exchange confirms the order's execution |
- `ping_url.py`: A Python script for measuring the response times of a given URL by sending multiple HTTP GET requests


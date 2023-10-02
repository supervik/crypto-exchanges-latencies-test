import csv
import logging
import os
import time
from enum import Enum

from hummingbot.connector.utils import split_hb_trading_pair
from hummingbot.core.data_type.common import OrderType, TradeType
from hummingbot.core.data_type.order_candidate import OrderCandidate
from hummingbot.core.event.events import BuyOrderCreatedEvent, OrderCancelledEvent, SellOrderCreatedEvent, \
    OrderFilledEvent
from hummingbot.strategy.script_strategy_base import Decimal, ScriptStrategyBase


class OrderState(Enum):
    PENDING_CREATE = 0
    CREATED = 1
    PENDING_CANCEL = 2
    CANCELED = 3
    PENDING_EXECUTE = 4
    EXECUTED = 5


class LatencyTest(ScriptStrategyBase):
    """
    This script measures the latency between order creation, execution, and cancellation on an exchange.
    It places both market and limit orders at regular intervals and logs the time taken for various states.
    """
    # Configuration parameters
    trading_pair = "BNB-ETH"
    connector_name = "binance"
    order_amount = Decimal("0.01")
    order_spread = Decimal("5")  # Percentage distance to place limit orders from the current price
    test_create_latency = True  # Flag to enable testing creation and cancellation latency
    test_execute_latency = True  # Flag to enable testing execution latency
    create_interval = 30  # Time interval (in seconds) between limit order creations
    execute_interval = 300  # Time interval (in seconds) between market order executions
    delay = 5  # Time delay (in seconds) to avoid multiple requests being sent simultaneously
    csv_file_id = "aws_tokyo"  # Identifier for distinct CSV filenames

    markets = {connector_name: {trading_pair}}

    # Variables to hold state at runtime
    create_timestamp = 0
    execute_timestamp = 0
    delay_timestamp = 0
    order_filled = False

    @property
    def connector(self):
        """Provides easy access to the associated connector."""
        return self.connectors[self.connector_name]

    @property
    def timestamp_now(self):
        """Returns the current timestamp in milliseconds."""
        return int(time.time() * 1e3)

    @property
    def filename(self):
        """Generates the filename for the CSV based on the connector name and CSV file ID."""
        return f"data/{self.connector_name}_{self.csv_file_id}_latency_test.csv"

    def on_tick(self):
        """Called regularly to check for order creation, execution, and cancellation conditions."""
        # Initialize execute_timestamp on the first tick
        if not self.execute_timestamp:
            self.execute_timestamp = self.current_timestamp + self.execute_interval

        # Prevent further actions if within the delay period
        if self.current_timestamp < self.delay_timestamp:
            return

        # Cancel any active orders after the delay has passed
        if self.get_active_orders(self.connector_name):
            self.delay_timestamp = self.current_timestamp + self.delay
            self.cancel_all_orders()
            return

        # Execute market order if conditions are met
        if self.test_execute_latency and self.current_timestamp > self.execute_timestamp:
            self.delay_timestamp = self.current_timestamp + self.delay
            self.execute_timestamp = self.current_timestamp + self.execute_interval
            self.order_filled = False
            self.place_order(is_maker=False)
            return

        # Place a limit order if conditions are met
        if self.test_create_latency and self.current_timestamp > self.create_timestamp:
            self.delay_timestamp = self.current_timestamp + self.delay
            self.create_timestamp = self.current_timestamp + self.create_interval
            self.place_order(is_maker=True)

    def cancel_all_orders(self):
        """Cancels all active orders on the exchange and logs the pre-transmission timestamp and status."""
        for order in self.get_active_orders(self.connector_name):
            self.save_to_csv(self.timestamp_now, order.client_order_id, OrderState.PENDING_CANCEL.name)
            self.cancel(self.connector_name, order.trading_pair, order.client_order_id)

    def place_order(self, is_maker):
        """
        Determines the appropriate order type and side, then sends the order to the exchange.

        Args:
        - is_maker (bool): Indicates if the order is a maker (limit) or taker (market) order.
        """
        order_side = self.get_order_side()
        order_type = OrderType.LIMIT if is_maker else OrderType.MARKET

        # Determine the order price based on the type and side
        if order_side == TradeType.BUY:
            current_price = self.connector.get_price(self.trading_pair, False)
            price_multiplier = Decimal(1 - self.order_spread / 100)
        else:
            current_price = self.connector.get_price(self.trading_pair, True)
            price_multiplier = Decimal(1 + self.order_spread / 100)

        order_price = current_price * price_multiplier if is_maker else current_price

        # Create an order candidate
        candidate = OrderCandidate(
            trading_pair=self.trading_pair,
            is_maker=is_maker,
            order_type=order_type,
            order_side=order_side,
            amount=self.order_amount,
            price=order_price
        )

        # Adjust the order candidate based on available funds and minimum thresholds
        candidate_adjusted = self.connector.budget_checker.adjust_candidate(candidate, all_or_none=False)

        if candidate_adjusted.amount != Decimal("0"):
            self.send_order_to_exchange(candidate_adjusted)
        else:
            self.log_with_clock(logging.INFO, f"Can't create {candidate.order_type} {candidate.order_side} order. "
                                              f"Not enough funds or amount is below threshold")

    def get_order_side(self):
        """
        Determines the side (BUY or SELL) for the next order based on the current account balances.

        Returns:
        - TradeType.BUY or TradeType.SELL depending on which asset balance is higher.
        """
        base, quote = split_hb_trading_pair(self.trading_pair)
        base_balance = self.connector.get_balance(base)
        quote_balance = self.connector.get_balance(quote)
        current_price = self.connector.get_price(self.trading_pair, False)
        base_balance_in_quote = base_balance * current_price
        return TradeType.BUY if base_balance_in_quote < quote_balance else TradeType.SELL

    def send_order_to_exchange(self, candidate):
        """Sends the order to the exchange and logs the pre-transmission timestamp and status."""
        time_before_order_sent = self.timestamp_now
        if candidate.order_side == TradeType.BUY:
            order_id = self.buy(self.connector_name, candidate.trading_pair, candidate.amount,
                                candidate.order_type, candidate.price)
        else:
            order_id = self.sell(self.connector_name, candidate.trading_pair, candidate.amount,
                                 candidate.order_type, candidate.price)

        status = OrderState.PENDING_CREATE if candidate.order_type == OrderType.LIMIT else OrderState.PENDING_EXECUTE
        self.save_to_csv(time_before_order_sent, order_id, status.name)

    def did_create_buy_order(self, event: BuyOrderCreatedEvent):
        """Logs the post-transmission timestamp when a confirmation of buy order created is received."""
        self.save_to_csv(self.timestamp_now, event.order_id, OrderState.CREATED.name)

    def did_create_sell_order(self, event: SellOrderCreatedEvent):
        """Logs the post-transmission timestamp when a confirmation of sell order created is received."""
        self.save_to_csv(self.timestamp_now, event.order_id, OrderState.CREATED.name)

    def did_cancel_order(self, event: OrderCancelledEvent):
        """Logs the post-transmission timestamp when a confirmation of order cancelled is received."""
        self.save_to_csv(self.timestamp_now, event.order_id, OrderState.CANCELED.name)

    def did_fill_order(self, event: OrderFilledEvent):
        """
        Logs the post-transmission timestamp when a confirmation of order is filled received.
        Ensures that only the first fill event for a specific order is logged.
        """
        if not self.order_filled:
            self.save_to_csv(self.timestamp_now, event.order_id, OrderState.EXECUTED.name)
            self.order_filled = True

    def save_to_csv(self, timestamp, order_id, status):
        """Appends the provided data to the CSV file. If the file doesn't exist, it creates one."""
        file_exists = os.path.exists(self.filename)

        with open(self.filename, 'a', newline='') as csvfile:
            fieldnames = ['Timestamp', 'Order_ID', 'Status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()

            writer.writerow({'Timestamp': timestamp, 'Order_ID': order_id, 'Status': status})

import asyncio
import logging
from math import isfinite
import sys
from typing import Dict
from datetime import datetime, timedelta, timezone
from xecution.common.enums import DataProvider, Exchange, KlineType, Mode, OrderSide, OrderType, Symbol
from xecution.models.order import ActiveOrder
from xecution.models.config import OrderConfig, RuntimeConfig
from xecution.models.topic import DataTopic, KlineTopic
from xecution.services.datasource.cryptoquant import CryptoQuantClient
from xecution.services.datasource.rexilion import RexilionClient
from xecution.services.exchange.binance_service import BinanceService
from xecution.services.exchange.bybit_service import BybitService
from xecution.services.exchange.okx_service import OkxService
from xecution.services.exchange.coinbase_service import CoinbaseService
from xecution.utils import utility

class BaseEngine:
    """Base engine that processes on_candle_closed and on_datasource_update."""
    def __init__(self, config: RuntimeConfig):
        self.config = config
        self.data_map = {}  # Local storage for kline and data source values
        self.binance_service = BinanceService(config, self.data_map)
        self.bybit_service = BybitService(config, self.data_map)
        self.okx_service = OkxService(config, self.data_map)
        self.coinbase_service = CoinbaseService(config, self.data_map)
        self.cryptoquant_client = CryptoQuantClient(config, self.data_map)
        self.rexilion_client = RexilionClient(config, self.data_map)
        # Track last processed timestamp for each data topic
        self._last_timestamps: Dict[str, int] = {
            topic.url: None for topic in self.config.datasource_topic
        }

    async def on_candle_closed(self, kline_topic: KlineTopic):
        """Handle closed candle events from the exchange."""

    async def on_order_update(self, order):
        """Handle order status updates."""

    async def on_datasource_update(self, datasource_topic):
        """Handle updates from external data sources."""
        logging.info(f"on_datasource_update: {datasource_topic}")
    
    async def on_active_order_interval(self, activeOrders: list[ActiveOrder]):
        """Process the list of open orders from periodic checks."""

    async def start(self):
        """Start services and run the main event loop based on mode."""
        try:
            if self.config.mode == Mode.Backtest:
                logging.info("Backtest started.")
            elif self.config.mode == Mode.Live:
                logging.info("Live started.")
            elif self.config.mode == Mode.Testnet:
                logging.info("Testnet started.")

            # Begin fetching kline data and process closed candles
            await self.get_klines(self.on_candle_closed)
            # Start listening to external data source updates
            if self.config.mode == Mode.Backtest:
                # Backtest: run the full history load, then exit
                await self.listen_data_source_update()
            # For live or testnet trading, set up real-time listeners
            if self.config.mode in (Mode.Live, Mode.Testnet):
                if self.config.exchange == Exchange.Binance:
                    await self.binance_service.check_connection()
                elif self.config.exchange == Exchange.Bybit:
                    await self.bybit_service.check_connection()
                asyncio.create_task(self.listen_data_source_update())
                await self.listen_order_status()
                asyncio.create_task(self.listen_open_orders_periodically())
                asyncio.create_task(self.dd_detector())
                while True:
                    await asyncio.sleep(1)  # Keep the loop alive
            else:
                await self.on_backtest_completed()
                logging.info("Backtest completed. Exiting.")
        except ConnectionError as e:
            logging.error(f"Connection check failed: {e}")
        
    async def place_order(self, order_config: OrderConfig):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.place_order(order_config)
        elif self.config.exchange == Exchange.Bybit:
            return await self.bybit_service.place_order(order_config)
        
    async def get_account_info(self):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.get_account_info()
        elif self.config.exchange == Exchange.Bybit:
            return await self.bybit_service.get_account_info()

    async def set_hedge_mode(self, is_hedge_mode: bool, symbol: Symbol):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.set_hedge_mode(is_hedge_mode)
        elif self.config.exchange == Exchange.Bybit:
            return await self.bybit_service.set_hedge_mode(is_hedge_mode, symbol)

    async def set_leverage(self, symbol: Symbol, leverage: int):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.set_leverage(symbol, leverage)
        elif self.config.exchange == Exchange.Bybit:
            return await self.bybit_service.set_leverage(symbol, leverage)
    
    async def get_position_info(self, symbol: Symbol):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.get_position_info(symbol)
        elif self.config.exchange == Exchange.Bybit:
            return await self.bybit_service.get_position_info(symbol)
    
    async def get_wallet_balance(self):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.get_wallet_balance()
        elif self.config.exchange == Exchange.Bybit:
            return await self.bybit_service.get_wallet_balance()

    async def get_current_price(self, symbol: Symbol):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.get_current_price(symbol)
        elif self.config.exchange == Exchange.Bybit:
            return await self.bybit_service.get_current_price(symbol)
        elif self.config.exchange == Exchange.Okx:
            return await self.okx_service.get_current_price(symbol)
        else:
            logging.error("Unknown exchange")
            return None
        
    async def get_order_book(self, symbol: Symbol):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.get_order_book(symbol)
        elif self.config.exchange == Exchange.Bybit:
            return await self.bybit_service.get_order_book(symbol)
        else:
            logging.error("Unknown exchange")
            return None

    async def listen_order_status(self):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.listen_order_status(self.on_order_update)
        elif self.config.exchange == Exchange.Bybit:
            return await self.bybit_service.listen_order_status(self.on_order_update)
        else:
            logging.error("Unknown exchange")
            return None
        
    async def get_open_orders(self):
        if self.config.exchange == Exchange.Binance:
            # Call BinanceService and pass the on_active_order_interval callback
            return await self.binance_service.get_open_orders(self.on_active_order_interval)
        elif self.config.exchange == Exchange.Bybit:
            # Call BinanceService and pass the on_active_order_interval callback
            return await self.bybit_service.get_open_orders(self.on_active_order_interval)
        else:
            logging.error("Unknown exchange")
            
    async def cancel_order(self, symbol: Symbol, client_order_id: str):
        if self.config.exchange == Exchange.Binance:
            return await self.binance_service.cancel_order(symbol, client_order_id)
        elif self.config.exchange == Exchange.Bybit:
            return await self.bybit_service.cancel_order(symbol, client_order_id)
        else:
            logging.error("Unknown exchange")
    
    async def listen_open_orders_periodically(self):
        """
        Every 60 seconds, call Binance's get_open_orders API, convert the
        returned open orders to ActiveOrder, and pass them to on_active_order_interval for processing.
        """
        while True:
            try:
                # Since get_open_orders internally uses on_active_order_interval,
                # we just await its completion here.
                await self.get_open_orders()
            except Exception as e:
                logging.error("Error retrieving open orders: %s", e)
            await asyncio.sleep(10)
            

    async def fetch_latest_datasource(self, topic, last_n: int = 1):
        """
        Provider-aware 'latest' fetch for a topic.
        Returns a list (possibly length==last_n) or [] if none.
        """
        if topic.provider == DataProvider.CRYPTOQUANT:
            return await self.cryptoquant_client.fetch(topic, last_n=last_n)
        elif topic.provider == DataProvider.REXILION:
            # Ensure your rexilion_client has a similar 'fetch(topic, last_n=...)' API.
            # If it's named differently (e.g., fetch_recent), adapt here.
            return await self.rexilion_client.fetch_all(topic, last_n)
        else:
            # Unknown provider; you can either no-op or route to a generic fetcher if you have one.
            return []

    async def fetch_full_datasource(self, topic):
        """
        Provider-aware 'full batch' fetch for a topic.
        Mirrors your Backtest behavior.
        """
        if topic.provider == DataProvider.CRYPTOQUANT:
            await self.cryptoquant_client.fetch_all_parallel(topic)
        elif topic.provider == DataProvider.REXILION:
            await self.rexilion_client.fetch_all(topic)
        else:
            # Unknown provider; nothing to do
            return

    async def listen_data_source_update(self):
        """
        Backtest mode: Fetch full history once per topic, then invoke
        on_datasource_update(topic) so handlers can access data_map.

        Live/Testnet mode (provider-aware like Backtest):
        - Seed with the most recent bar per topic (CryptoQuant/Rexilion),
        - Align to the next 30-second boundary,         
        - Every 30s: fetch most recent per topic; if new ts appears:  
            • wait briefly to ensure completion,
            • fetch full batch using the same provider-specific path as Backtest,
            • invoke on_datasource_update(topic),
            • update last processed ts.
        """
        logging.info("Data source listening has started.")

        # ───────────────────────── Backtest: one-shot full history ─────────────────────────
        if self.config.mode == Mode.Backtest:
            for topic in self.config.datasource_topic:
                if topic.provider == DataProvider.CRYPTOQUANT:
                    await self.cryptoquant_client.fetch_all_parallel(topic)
                elif topic.provider == DataProvider.REXILION:
                    await self.rexilion_client.fetch_all(topic)
                await self.on_datasource_update(topic)
            return

        # ───────────────────────── Live/Testnet: initial seed ─────────────────────────
        self._last_timestamps = getattr(self, "_last_timestamps", {})
        for topic in self.config.datasource_topic:
            try:
                latest = await self.fetch_latest_datasource(topic, last_n=1)
                if latest:
                    self._last_timestamps[topic] = int(latest[-1].get("start_time", 0))  # defensive cast
            except Exception as e:
                logging.error("Initial seed failed for %s (%s): %s", topic.url, topic.provider, e)

        # Align to the start of the next 30-second boundary         
        now = datetime.now(timezone.utc)                               
        secs = now.second                                           
        to_next_30 = 30 - (secs % 30)                               
        next_boundary = (now + timedelta(seconds=to_next_30)).replace(microsecond=0)  
        await asyncio.sleep(max(0.0, (next_boundary - now).total_seconds()))          

        # ───────────────────────── Periodic loop (every 30s) ───────────────────────── 
        period = 30.0                                                  
        while True:
            cycle_start = datetime.now(timezone.utc)

            for topic in self.config.datasource_topic:
                try:
                    latest = await self.fetch_latest_datasource(topic, last_n=1)
                    if not latest:
                        continue

                    ts = int(latest[-1].get("start_time", 0))
                    last_ts = int(self._last_timestamps.get(topic, 0))

                    if ts > last_ts:
                        # Wait a bit to ensure the record is fully written/consistent across providers
                        await asyncio.sleep(10)

                        # Fetch the full batch using the provider-specific path (mirrors Backtest)
                        await self.fetch_full_datasource(topic)

                        # Notify handlers that data_map is updated
                        await self.on_datasource_update(topic)

                        # Mark progress
                        self._last_timestamps[topic] = ts

                except Exception as e:
                    logging.error("Error fetching %s (%s): %s", getattr(topic, "url", "<no-url>"), topic.provider, e)
            # Sleep until the next 30-second boundary, compensating for drift         
            elapsed = (datetime.now(timezone.utc) - cycle_start).total_seconds()      
            sleep_for = period - (elapsed % period)                                   
            await asyncio.sleep(max(0.0, sleep_for))                                 

    async def on_backtest_completed(self):
        """ Handling after all the data retrieving has done. """

    async def get_klines(self, on_candle_closed):
        """
        Call Binance REST or WebSocket to retrieve kline (candlestick) data.
        """
        for kline_topic in self.config.kline_topic:
            if kline_topic.klineType in (KlineType.Binance_Futures, KlineType.Binance_Spot):
                await self.binance_service.get_klines(kline_topic, self.on_candle_closed)
            elif kline_topic.klineType == KlineType.Coinbase_Spot:
                await self.coinbase_service.get_klines(kline_topic, self.on_candle_closed)
            elif kline_topic.klineType in (KlineType.Bybit_Spot, KlineType.Bybit_Futures):
                await self.bybit_service.get_klines(kline_topic, self.on_candle_closed)


    async def dd_detector(self):
        logging.info("DD detector is alive.")

        # ── init: align to :30s
        now = datetime.now(timezone.utc)
        target = now.replace(second=30, microsecond=0)
        if now.second >= 30:
            target += timedelta(minutes=1)
        await asyncio.sleep(max(0.0, (target - now).total_seconds()))

        # ── init: peak balance (only once, inline)
        if not hasattr(self, "_peak_balance") or self._peak_balance is None:
            try:
                latest0 = float(await self.get_wallet_balance())
            except Exception:
                latest0 = 0.0
            baseline = self.config.initial_capital
            if baseline is None or not isfinite(baseline) or baseline <= 0:
                baseline = latest0
            self._peak_balance = max(float(baseline), float(latest0))

        while True:
            try:
                logging.debug("dd detector checking...")
                latest_wallet_balance = float(await self.get_wallet_balance())
                if not isfinite(latest_wallet_balance) or latest_wallet_balance <= 0:
                    raise ValueError(f"Non-finite wallet balance: {latest_wallet_balance}")

                # ── update peak (captures profits or deposits)
                self._peak_balance = max(self._peak_balance, latest_wallet_balance)

                # ── drawdown from peak
                dd = 1.0 - (latest_wallet_balance / self._peak_balance)

                if dd >= self.config.max_dd:
                    logging.error(
                        f"DD detector triggered. dd={dd:.4f} "
                        f"latest={latest_wallet_balance:.2f} peak={self._peak_balance:.2f}"
                    )
                    msg = (
                    "🚨 *Drawdown Triggered*\n"
                    f"• Bot: {self.config.bot_name}\n"
                    f"• Time (UTC): {datetime.now(timezone.utc)}\n"
                    f"• DD: {dd*100:.2f}%  (limit {self.config.max_dd*100:.2f}%)\n"
                    f"• Latest Balance: {latest_wallet_balance:.4f}\n"
                    f"• Peak Balance:   {self._peak_balance:.4f}\n"
                    "Action: Cancel order, close all the position and shut down bot."
                    )
                    try:
                        await self.cancel_order_position()  # close out before exit
                        utility.send_notification_telegram(msg,"-4796978041","8429019980:AAHHrfVx_T1opgAXy5jC87utsgYc5oBDucM")
                    except Exception as ce:
                        logging.error(f"Error while closing positions: {ce}")
                    sys.exit(0)

            except Exception as e:
                logging.error(f"Error in drawdown detector: {e}")

            # keep running exactly at :30 each minute
            await asyncio.sleep(60)
                
    async def cancel_order_position(self):
        try:
            logging.info("Cancelling all active order and position.")
            if self.config.exchange == Exchange.Binance:
                market_type = KlineType.Binance_Futures
                # Call BinanceService and pass the on_active_order_interval callback
                active_orders = await self.binance_service.get_open_orders()
                for order in active_orders:
                    await self.cancel_order(order.symbol,order.client_order_id)
            elif self.config.exchange == Exchange.Bybit:
                market_type = KlineType.Bybit_Futures
                # Call BinanceService and pass the on_active_order_interval callback
                active_orders = await self.bybit_service.get_open_orders()
                for order in active_orders:
                    await self.cancel_order(order.symbol,order.client_order_id)
            else:
                logging.error("Unknown exchange")
            for symbol in (Symbol.BTCUSDT, Symbol.ETHUSDT, Symbol.SOLUSDT):
                position = await self.get_position_info(symbol)
                if position.long.quantity > 0:
                    await self.place_order(OrderConfig(
                                market_type=market_type, symbol=symbol,
                                side=OrderSide.SELL, order_type=OrderType.MARKET,
                                quantity=position.long.quantity,
                            ))
                elif position.short.quantity > 0:
                    await self.place_order(OrderConfig(
                                market_type=market_type, symbol=symbol,
                                side=OrderSide.BUY, order_type=OrderType.MARKET,
                                quantity=position.short.quantity,
                            ))
        except Exception as e:
            logging.error(f"Failed to cancel order and position: {e}")
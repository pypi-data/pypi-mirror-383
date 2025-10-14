import json
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone
from xecution.common.datasource_constants import CryptoQuantConstants
from xecution.models.config import RuntimeConfig
from xecution.models.topic import DataTopic, DataProvider
from xecution.services.connection.restapi import RestAPIClient

class CryptoQuantClient:
    def __init__(self, config: RuntimeConfig, data_map: dict):
        self.config      = config
        self.rest_client = RestAPIClient()
        self.data_map    = data_map
        self.headers     = {
            'Authorization': f'Bearer {self.config.cryptoquant_api_key}',
        }

    async def fetch(self, data_topic: DataTopic, last_n: int = 3):
        """
        Fetch only the last `last_n` records for `data_topic` (no `to` param).
        """
        # parse path and base params
        if '?' in data_topic.url:
            path, qs = data_topic.url.split('?', 1)
            base_params = dict(part.split('=', 1) for part in qs.split('&'))
        else:
            path = data_topic.url
            base_params = {}

        url = CryptoQuantConstants.BASE_URL + path
        params = {**base_params, 'limit': last_n}

        try:
            raw = await self.rest_client.request(
                method='GET', url=url, params=params, headers=self.headers,timeout=50
            )
        except Exception as e:
            logging.error(f"[{datetime.now()}] Error fetching last {last_n} for {data_topic.url}: {e}")
            return []

        result = raw.get('result', raw)
        data   = result.get('data') if isinstance(result, dict) else result
        items  = data if isinstance(data, list) else [data]

        processed = []
        for item in items or []:
            dt_str = item.get('datetime') or item.get('date')
            if dt_str:
                try:
                    item['start_time'] = self.parse_datetime_to_timestamp(dt_str)
                except ValueError as ex:
                    logging.warning(f"Date parsing failed ({dt_str}): {ex}")
            processed.append(item)

        processed.sort(key=lambda x: x.get('start_time', 0))
        final = processed[-last_n:]

        self.data_map[data_topic] = final
        return final

    async def fetch_all_parallel(self, data_topic: DataTopic):
        """
        Fetch up to `config.data_count` bars ending now.
        - Single GET for most endpoints.
        - Batched GETs only for 'stablecoins-ratio'.
        - Post-process: flatten → sort → dedupe → (minimal) cadence gap-fill → forward-fill Nones.
        - Logs a WARNING for each carried-forward (cloned) bar and a summary count.
        """
        limit      = self.config.data_count
        base_limit = 1000
        windows    = -(-limit // base_limit)  # ceil division
        end        = datetime.now(timezone.utc)

        # parse URL and base params
        if '?' in data_topic.url:
            path, qs = data_topic.url.split('?', 1)
            base_params = dict(part.split('=') for part in qs.split('&'))
        else:
            path = data_topic.url
            base_params = {}
        url = CryptoQuantConstants.BASE_URL + path

        session = aiohttp.ClientSession()
        try:
            if not (
                data_topic.provider is DataProvider.CRYPTOQUANT and
                'stablecoins-ratio' in data_topic.url
            ):
                # single-fetch branch
                try:
                    async with session.get(url, params={**base_params, 'limit': limit, 'format': 'json'}, headers=self.headers) as resp:
                        resp.raise_for_status()
                        raw = await resp.json()
                except Exception as e:
                    logging.error(f"[{datetime.now()}] Error fetching data for {data_topic.url}: {e}")
                    batches = [[]]
                else:
                    result = raw.get('result', raw)
                    data   = result.get('data') if isinstance(result, dict) else result
                    items  = data if isinstance(data, list) else [data]
                    # attach timestamps
                    batch = []
                    for item in items or []:
                        dt_str = item.get('datetime') or item.get('date')
                        if dt_str:
                            try:
                                item['start_time'] = self.parse_datetime_to_timestamp(dt_str)
                            except ValueError as ex:
                                logging.warning(f"Date parsing failed ({dt_str}): {ex}")
                        batch.append(item)
                    batches = [batch]
            else:
                # batch-fetch branch for stablecoins-ratio
                async def fetch_batch(to_ts: datetime):
                    from_str = to_ts.strftime('%Y%m%dT%H%M%S')
                    params   = {**base_params, 'limit': base_limit, 'to': from_str, 'format': 'json'}
                    try:
                        async with session.get(url, params=params, headers=self.headers) as resp:
                            resp.raise_for_status()
                            raw = await resp.json()
                    except Exception as e:
                        logging.error(f"[{datetime.now()}] Parallel fetch error: {e}")
                        return []

                    result = raw.get('result', raw.get('data', raw))
                    if isinstance(result, dict) and 'data' in result:
                        result = result['data']
                        if isinstance(result, str):
                            result = json.loads(result)
                    if isinstance(result, dict):
                        result = [result]

                    recs = []
                    for item in result or []:
                        dt_str = item.get('datetime')
                        if dt_str:
                            try:
                                item['start_time'] = self.parse_datetime_to_timestamp(dt_str)
                            except ValueError as ex:
                                logging.warning(f"Date parsing failed ({dt_str}): {ex}")
                                continue
                        recs.append(item)
                    return recs

                tasks   = [fetch_batch(end - timedelta(hours=i * base_limit)) for i in range(windows)]
                batches = await asyncio.gather(*tasks)
        finally:
            await session.close()

        # === common post-processing: flatten, sort, dedupe ===
        flat = [rec for batch in batches for rec in batch if isinstance(rec, dict)]
        flat.sort(key=lambda x: x.get('start_time', 0))
        deduped = {x['start_time']: x for x in flat if 'start_time' in x}

        vals = list(deduped.values())
        if isinstance(limit, int) and limit > 0:
            vals = vals[-limit:]  # keep newest `limit` rows (no buffer)

        # --- MINIMAL ADD: detect cadence (hour/day) + fill gaps using previous record ---
        HOUR_MS = 3_600_000
        DAY_MS  = 86_400_000

        def _parse_step_ms(bp: dict, sample: list[dict]) -> int:
            # Prefer explicit window/interval/timeframe
            try:
                key = (bp.get("window") or bp.get("interval") or bp.get("timeframe") or "").lower()
            except Exception:
                key = ""
            if key.endswith("d"):
                try: return (int(key[:-1] or "1")) * DAY_MS
                except: pass
            if key.endswith("h"):
                try: return (int(key[:-1] or "1")) * HOUR_MS
                except: pass
            # Infer from first two timestamps; snap to hour/day if within 10%
            ts = [r.get("start_time") for r in sample if isinstance(r.get("start_time"), (int, float))]
            ts = sorted(set(ts))
            if len(ts) >= 2:
                d = ts[1] - ts[0]
                if abs(d - DAY_MS)  <= 0.1 * DAY_MS:  return DAY_MS
                if abs(d - HOUR_MS) <= 0.1 * HOUR_MS: return HOUR_MS
            return HOUR_MS  # default

        step_ms = _parse_step_ms(base_params, vals)

        # Ensure ascending order for gap detection
        vals.sort(key=lambda x: x.get('start_time', 0))

        # Insert ghost bars for missing steps; warn per carried-forward bar
        filled_sequence = []
        prev = None
        carried_count = 0
        for rec in vals:
            cur_ts = rec.get('start_time')
            if prev is not None and isinstance(cur_ts, (int, float)) and isinstance(prev.get('start_time'), (int, float)):
                expected = prev['start_time'] + step_ms
                while cur_ts > expected:
                    ghost = prev.copy()
                    ghost['start_time'] = expected
                    if 'end_time' in ghost and isinstance(ghost['end_time'], (int, float)):
                        ghost['end_time'] = expected + step_ms
                    if 'datetime' in ghost:
                        ghost['datetime'] = datetime.fromtimestamp(expected / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                    ghost['_filled_from_prev'] = True
                    filled_sequence.append(ghost)
                    carried_count += 1
                    logging.warning(
                        f"Gap detected at {expected} — inserted carried-forward bar cloned from {prev.get('start_time')}"
                    )
                    prev = ghost
                    expected += step_ms
            filled_sequence.append(rec)
            prev = rec

        # Re-enforce exact `limit` newest rows after gap-fill (optional but practical)
        if isinstance(limit, int) and limit > 0 and len(filled_sequence) > limit:
            filled_sequence = filled_sequence[-limit:]

        if carried_count:
            logging.warning(f"Total carried-forward bars inserted: {carried_count}")

        # ───────────── Forward-fill None fields within the sequence ─────────────
        filled = []
        prev = None
        for rec in filled_sequence:
            if prev is not None:
                for k, v in rec.items():
                    if v is None:
                        logging.warning(
                            f"Missing value for '{k}' at start_time: {rec.get('start_time')} — forward-filled from previous"
                        )
                        rec[k] = prev.get(k)
            else:
                for k, v in rec.items():
                    if v is None:
                        logging.error(f"Missing value for '{k}' at start_time {rec.get('start_time')}")
            filled.append(rec)
            prev = rec

        self.data_map[data_topic] = filled
        return filled

    def parse_datetime_to_timestamp(self, dt_str: str) -> int:
        for fmt in (
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
        ):
            try:
                dt = datetime.strptime(dt_str, fmt).replace(tzinfo=timezone.utc)
                return int(dt.timestamp() * 1000)
            except ValueError:
                continue
        try:
            clean = dt_str.rstrip('Z')
            dt    = datetime.fromisoformat(clean)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp() * 1000)
        except Exception:
            raise ValueError(f"Unrecognized date format: {dt_str}")

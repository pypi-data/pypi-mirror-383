import re
import time
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Callable

import requests

ADDRESS_RX = re.compile(r"^kaspa:[a-z0-9]{61,63}$")
PAGE_SIZE = 50

# ---------- API ----------
def fetch_transactions_page(address: str, *, limit=PAGE_SIZE, offset=0) -> List[Dict[str, Any]]:
    url = f"https://api.kaspa.org/addresses/{address}/full-transactions"
    headers = {"accept": "application/json"}
    params = {"limit": limit, "offset": offset, "resolve_previous_outpoints": "full"}
    r = requests.get(url, headers=headers, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("transactions") or data.get("items") or []
    return []

def fetch_all_transactions(address: str, *, page_size=PAGE_SIZE, max_pages=200) -> List[Dict[str, Any]]:
    all_txs: List[Dict[str, Any]] = []
    offset = 0
    for _ in range(max_pages):
        page = fetch_transactions_page(address, limit=page_size, offset=offset) or []
        if not page:
            break
        all_txs.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return all_txs

# ---------- Parsers ----------
def parse_tx_id(tx: Dict[str, Any]) -> str:
    return str(tx.get("transaction_id") or tx.get("hash") or "unknown")

def parse_time(tx: Dict[str, Any]) -> Optional[int]:
    t = tx.get("block_time") or tx.get("timestamp")
    try:
        t = int(t)
        return t if t >= 10**12 else t * 1000  # ms
    except Exception:
        return None

def format_time_ms(t_ms: Optional[int]) -> str:
    if t_ms is None:
        return "no-time"
    dt = datetime.fromtimestamp(t_ms/1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")

def norm(s: Optional[str]) -> str:
    return s.lower() if isinstance(s, str) else ""

def net_amount_kas_for_address(tx: Dict[str, Any], address: str) -> float:
    addr = norm(address)
    out_total = 0
    for o in tx.get("outputs") or []:
        o_addr = norm(o.get("script_public_key_address") or o.get("address"))
        if o_addr == addr:
            try:
                out_total += int(o.get("amount", 0))
            except Exception:
                pass
    in_total = 0
    for i in tx.get("inputs") or []:
        i_addr = norm(i.get("previous_outpoint_address") or i.get("address"))
        val = i.get("previous_outpoint_amount") or i.get("value")
        if i_addr == addr and val is not None:
            try:
                in_total += int(val)
            except Exception:
                pass
    return (out_total - in_total) / 1e8

# ---------- Modes ----------
def run_historical(address: str, page_size: int, *, printer=print):
    """Print ALL historical transactions (oldest→newest) and exit."""
    txs = fetch_all_transactions(address, page_size=page_size)
    if not txs:
        printer("📜 No transactions found.")
        return 0
    txs.sort(key=lambda tx: parse_time(tx) or 0)
    for tx in txs:
        txid = parse_tx_id(tx)
        amt = net_amount_kas_for_address(tx, address)
        t_ms = parse_time(tx)
        printer(f"📜 {amt:.8f} KAS | txid: {txid} | {format_time_ms(t_ms)}")
    return 0

# Callback signature:
# on_tx(txid: str, amount_kas: float, time_ms: Optional[int], tx: Dict[str, Any]) -> None
OnTx = Callable[[str, float, Optional[int], Dict[str, Any]], None]

def run_live(address: str, interval: int, page_size: int, *, on_tx: OnTx, printer=print):
    """
    Live mode (no side-effects here beyond calling on_tx).
    """
    if not ADDRESS_RX.match(address):
        printer(f"Invalid address: {address}")
        return 1

    current = fetch_all_transactions(address, page_size=page_size)
    seen = {parse_tx_id(tx) for tx in current if parse_tx_id(tx)}

    printer("🐸🔮 Peering into the orb... (Ctrl+C to stop)")
    try:
        while True:
            offset = 0
            while True:
                page = fetch_transactions_page(address, limit=page_size, offset=offset) or []
                if not page:
                    break
                for tx in page:
                    txid = parse_tx_id(tx)
                    if not txid or txid in seen:
                        continue
                    seen.add(txid)
                    amt = net_amount_kas_for_address(tx, address)
                    t_ms = parse_time(tx)
                    on_tx(txid, amt, t_ms, tx)
                if len(page) < page_size:
                    break
                offset += page_size
            time.sleep(max(1, interval))
    except KeyboardInterrupt:
        printer("\n🐸💨 The frog vanishes in a puff of smoke...")
        return 0
import os
import json
from datetime import datetime, timezone
from typing import Optional

from .sentry import format_time_ms


def write_receipt(
    dirpath: str,
    *,
    address: str,
    txid: str,
    amount_kas: float,
    time_ms: Optional[int],
    fmt: str = "txt",
):
    os.makedirs(dirpath, exist_ok=True)
    ext = "json" if fmt == "json" else "txt"

    short_txid = txid[:10]
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    fname = f"receipt_{date_str}_{short_txid}.{ext}"

    path = os.path.join(dirpath, fname)

    if os.path.exists(path):
        return path  # don't overwrite

    if fmt == "json":
        payload = {
            "schema": "kasmage.receipt@1",
            "address": address,
            "txid": txid,
            "amount_kas": float(f"{amount_kas:.8f}"),
            "time_utc": format_time_ms(time_ms),
            "issued_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"),
            "generator": "kasmage",
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    else:
        body = (
            "Payment Receipt\n"
            f"Address: {address}\n"
            f"Amount:  {amount_kas:.8f} KAS\n"
            f"TxID:    {txid}\n"
            f"Time:    {format_time_ms(time_ms)}\n"
            f"Issued:  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            "Conjured by: Kasmage 🪄\n"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)

    return path
import json
from pathlib import Path
from datetime import datetime

ORDERS_FILE = Path("orders.json")

def save_order(order: dict):
    """Append an order dict to orders.json (create file if missing)."""
    orders = []
    if ORDERS_FILE.exists():
        try:
            with ORDERS_FILE.open('r', encoding='utf-8') as f:
                orders = json.load(f)
        except Exception:
            orders = []
    order['created_at'] = datetime.utcnow().isoformat() + 'Z'
    orders.append(order)
    with ORDERS_FILE.open('w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)
    return True

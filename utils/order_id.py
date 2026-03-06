import random
import string
from datetime import datetime


def generate_order_id() -> str:
    date_str    = datetime.now().strftime("%Y%m%d")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"CRB-{date_str}-{random_part}"

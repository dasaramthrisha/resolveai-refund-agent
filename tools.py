import json
from datetime import date


def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_order_details(order_id):
    orders = load_json("data/orders.json")
    return orders.get(order_id, {"error": "Order not found"})


def check_refund_policy(order_id):
    order = get_order_details(order_id)
    if "error" in order:
        return order
    policy = load_json("data/refund_policy.json")
    delivered = date.fromisoformat(order["delivered_on"])
    days_since = (date.today() - delivered).days
    return {
        "days_since_delivery": days_since,
        "within_window": days_since <= policy["return_window_days"],
        "auto_approve_limit": policy["auto_approve_limit"],
        "within_auto_limit": order["price"] <= policy["auto_approve_limit"],
    }


def get_customer_history(customer_id):
    customers = load_json("data/customers.json")
    return customers.get(customer_id, {"error": "Customer not found"})


def run_fraud_check(order_id):
    order = get_order_details(order_id)
    if "error" in order:
        return order
    customer = get_customer_history(order["customer_id"])
    if "error" in customer:
        return customer
    if customer["past_orders"] == 0:
        return {"refund_rate": 0, "risk": "medium"}
    refund_rate = customer["past_refunds"] / customer["past_orders"]
    risk = "high" if refund_rate > 0.5 else "low"
    return {"refund_rate": round(refund_rate, 2), "risk": risk}


if __name__ == "__main__":
    for oid in ["ORD1001", "ORD1002"]:
        print("---", oid, "---")
        print("Order:   ", get_order_details(oid))
        print("Policy:  ", check_refund_policy(oid))
        print("Fraud:   ", run_fraud_check(oid))
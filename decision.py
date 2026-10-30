from tools import get_order_details, check_refund_policy, run_fraud_check


def decide_refund(order_id):
    order = get_order_details(order_id)
    if "error" in order:
        return {"decision": "reject", "confidence": 0.99, "reason": "Order not found"}

    policy = check_refund_policy(order_id)
    fraud = run_fraud_check(order_id)

    if not policy["within_window"]:
        return {
            "decision": "reject",
            "confidence": 0.95,
            "reason": f"Outside return window ({policy['days_since_delivery']} days since delivery)",
        }
    if fraud["risk"] == "high":
        return {"decision": "escalate", "confidence": 0.60, "reason": "High fraud risk, needs human review"}
    if not policy["within_auto_limit"]:
        return {"decision": "escalate", "confidence": 0.70, "reason": "Amount above auto-approve limit"}

    return {"decision": "approve", "confidence": 0.92, "reason": "Within window, low risk, within limit"}


if __name__ == "__main__":
    for oid in ["ORD1001", "ORD1002", "ORD1003", "ORD1004", "ORD9999"]:
        print(oid, decide_refund(oid))
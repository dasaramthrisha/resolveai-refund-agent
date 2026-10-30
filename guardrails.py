import re
from decision import decide_refund


def extract_order_id(message):
    match = re.search(r"ORD\d+", message.upper())
    return match.group(0) if match else None


def extract_decision(reply):
    match = re.search(r"DECISION:\s*(approve|reject|escalate)", reply, re.IGNORECASE)
    return match.group(1).lower() if match else None


def _base_guardrails(message, reply):
    order_id = extract_order_id(message)
    ai_decision = extract_decision(reply)

    if order_id is None:
        return {"final": "escalate", "note": "No order ID found, sent to a human"}
    if ai_decision is None:
        return {"final": "escalate", "note": "AI gave no clear decision, sent to a human"}

    rule = decide_refund(order_id)

    # Hard policy rejects (outside return window, unknown order) are decided by the rules
    if rule["decision"] == "reject":
        if ai_decision == "approve":
            return {
                "final": "reject",
                "note": f"GUARDRAIL: AI tried to approve, but rules say reject ({rule['reason']})",
            }
        return {"final": "reject", "note": f"Rules: {rule['reason']}"}

    if ai_decision == rule["decision"]:
        return {"final": ai_decision, "note": "AI and rules agree"}
    if ai_decision == "approve":
        return {
            "final": rule["decision"],
            "note": f"GUARDRAIL: AI tried to approve, but rules say {rule['decision']} ({rule['reason']})",
        }
    return {"final": "escalate", "note": "AI and rules disagree, sent to a human"}


def apply_guardrails(message, reply, analysis=None, photo=None):
    result = _base_guardrails(message, reply)

    if result["final"] == "approve":
        if analysis and analysis.get("reason") == "unclear":
            return {"final": "escalate", "note": "Customer did not explain the problem, sent to a human"}
        if (
            photo
            and photo.get("damage_visible") is False
            and analysis
            and analysis.get("reason") in ("damaged", "defective")
        ):
            return {"final": "escalate", "note": "Photo shows no visible damage, sent to a human"}
    return result
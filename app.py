import threading
import webbrowser
from flask import Flask, request, jsonify, render_template
from agent import run_agent
from analyzer import analyze_complaint
from guardrails import apply_guardrails
from logger import log_decision, read_logs

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/refund", methods=["POST"])
def refund():
    message = (request.get_json() or {}).get("message", "").strip()
    if not message:
        return jsonify({"error": "Please enter a message"}), 400
    analysis = analyze_complaint(message)
    reply = run_agent(message)
    result = apply_guardrails(message, reply, analysis)
    log_decision(message, analysis, reply, result)
    return jsonify({
        "final": result["final"],
        "note": result["note"],
        "reply": reply,
        "reason": analysis.get("reason"),
    })


@app.route("/api/logs")
def logs():
    return jsonify(read_logs())


if __name__ == "__main__":
    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(port=5000)
from flask import Flask, render_template, request, jsonify
import socket
from scanner import scan

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def start_scan():
    data = request.get_json() or {}
    target = str(data.get("target", "")).strip()

    try:
        start_port = int(data.get("start_port", 1))
        end_port = int(data.get("end_port", 100))
    except (TypeError, ValueError):
        return jsonify({"error": "Ports must be numbers."}), 400

    if not target:
        return jsonify({"error": "Enter a target."}), 400
    if not 1 <= start_port <= 65535:
        return jsonify({"error": "Invalid starting port."}), 400
    if not 1 <= end_port <= 65535:
        return jsonify({"error": "Invalid ending port."}), 400
    if start_port > end_port:
        return jsonify({"error": "Starting port cannot exceed ending port."}), 400
    if end_port - start_port > 1000:
        return jsonify({"error": "Keep the range at 1000 ports or fewer."}), 400

    try:
        resolved_ip = socket.gethostbyname(target)
    except socket.gaierror:
        return jsonify({"error": "Could not resolve target."}), 400

    results = scan(resolved_ip, start_port, end_port)
    return jsonify({"target": target, "ip": resolved_ip, "results": results})

if __name__ == "__main__":
    app.run(debug=True)

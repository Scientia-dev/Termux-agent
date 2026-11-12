
import os, json, subprocess, requests
from flask import Flask, render_template, request, jsonify

# ---------- config ----------
API_KEY = os.environ.get("GROQ_API_KEY", "")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"

if not API_KEY:
    raise SystemExit("GROQ_API_KEY not set. Run: export GROQ_API_KEY='gsk_...'")

SYSTEM = """You are a coding agent running on Android in Termux.
You can run terminal commands and read/write files using tools.
Work in small safe steps. Never run destructive commands (rm -rf, etc.).
Never touch files outside the current folder. When done, summarize what you did."""

# ---------- tools ----------
tools = [
    {"type": "function", "function": {
        "name": "run_terminal",
        "description": "Run a shell command in Termux and return output",
        "parameters": {"type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"]}}},
    {"type": "function", "function": {
        "name": "write_file",
        "description": "Write text content to a file",
        "parameters": {"type": "object",
            "properties": {"path": {"type": "string"},
                           "content": {"type": "string"}},
            "required": ["path", "content"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a file and return its content",
        "parameters": {"type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"]}}},
]

def run_terminal(command):
    print(f"\n[run] {command}")
    try:
        r = subprocess.run(command, shell=True, capture_output=True,
                           text=True, timeout=60)
        return (r.stdout + r.stderr)[:4000]
    except Exception as e:
        return f"error: {e}"

def write_file(path, content):
    print(f"\n[write] {path}")
    with open(path, "w") as f:
        f.write(content)
    return f"wrote {path} ({len(content)} chars)"

def read_file(path):
    print(f"\n[read] {path}")
    try:
        with open(path) as f:
            return f.read()[:4000]
    except Exception as e:
        return f"error: {e}"

# ---------- llm + loop ----------
def call_llm(messages):
    r = requests.post(API_URL,
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": "application/json"},
        json={"model": MODEL, "messages": messages,
              "tools": tools, "tool_choice": "auto"},
        timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]

def agent(user_msg):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_msg}]
    for _ in range(12):
        msg = call_llm(messages)
        messages.append(msg)
        if not msg.get("tool_calls"):
            return msg.get("content", "(no answer)")
        for call in msg["tool_calls"]:
            name = call["function"]["name"]
            try:
                args = json.loads(call["function"]["arguments"])
            except Exception:
                args = {}
            if name == "run_terminal":
                result = run_terminal(args.get("command", ""))
            elif name == "write_file":
                result = write_file(args.get("path", ""), args.get("content", ""))
            elif name == "read_file":
                result = read_file(args.get("path", ""))
            else:
                result = f"unknown tool {name}"
            messages.append({"role": "tool",
                             "tool_call_id": call["id"],
                             "content": result})
    return "stopped: too many steps"

# ---------- web ----------
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()
    if not user_input:
        return jsonify({"response": "Please type something."})
    try:
        return jsonify({"response": agent(user_input)})
    except requests.HTTPError as e:
        return jsonify({"response": f"API error: {e}"})
    except Exception as e:
        return jsonify({"response": f"Error: {e}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

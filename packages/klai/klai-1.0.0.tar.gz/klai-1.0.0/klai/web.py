from flask import Flask, render_template, request, jsonify, url_for, redirect, Response
from pathlib import Path
import subprocess
import os
import signal
import datetime
import json
import time
import logging
import sys

from . import db
from . import config
from .client import AIClient, KlaiError

# --- App Setup ---
APP_DIR = Path.home() / ".config" / "klai"
PID_FILE = APP_DIR / "web.pid"
LOG_FILE = APP_DIR / "klai_web.log"
app = Flask(__name__)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s [%(pathname)s:%(lineno)d]')

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)): return obj.isoformat()
        return super().default(obj)
app.json_encoder = CustomJSONEncoder

# --- Error Handling ---
@app.errorhandler(Exception)
def handle_api_error(e):
    """Log all exceptions and return a JSON error."""
    app.logger.error(f"An unhandled exception occurred: {e}", exc_info=True)
    return jsonify(error=str(e)), 500

# --- HTML Routes ---
@app.route("/")
def index(): return render_template("index.html")

@app.route("/conversation/<int:conversation_id>")
def conversation_page(conversation_id):
    # Redirect to the SPA-style URL for direct access.
    return redirect(url_for('index', _anchor=f"/conversation/{conversation_id}"))

@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route("/new")
def new_conversation_api():
    """Creates a new conversation and returns its ID for client-side redirect."""
    cfg = config.get_config()
    # The default_model in config is the full handle, e.g., "openai/gpt-4o"
    model_handle = cfg.get("default_model")
    if not model_handle:
        # Fallback if default_model is not set for some reason
        model_handle = "ollama/llama3"
    conv_id = db.create_conversation(model=model_handle, system_prompt="You are a helpful assistant.")
    return jsonify(id=conv_id)

@app.route("/logs")
def logs_page():
    if not LOG_FILE.exists(): return "No logs yet."
    with open(LOG_FILE, "r") as f: logs = f.read()
    return Response(logs, mimetype="text/plain")

# --- API Routes ---
@app.route("/api/providers")
def api_get_providers():
    """Returns the provider configuration."""
    return jsonify(config.get_config())

@app.route("/api/conversations")
def api_get_conversations():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    conversations = db.list_conversations(page=page, per_page=25, search=search)
    return jsonify([dict(row._mapping) for row in conversations])

@app.route("/api/conversation/<int:conversation_id>")
def api_get_conversation_details(conversation_id):
    conv = db.get_conversation(conversation_id)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404
    return jsonify(dict(conv._mapping))

@app.route("/api/conversation/<int:conversation_id>/messages")
def api_get_messages(conversation_id):
    messages_rows = db.get_active_branch(conversation_id)
    messages = [dict(row._mapping) for row in messages_rows]
    return jsonify(messages)

@app.route("/api/conversation/<int:conversation_id>/stream")
def sse_stream(conversation_id):
    def event_stream():
        last_id = 0
        while True:
            try:
                new_messages = db.get_new_messages(conversation_id, last_id)
                if new_messages:
                    last_id = new_messages[-1].id
                    for msg in new_messages:
                        yield f"data: {json.dumps(dict(msg._mapping), cls=CustomJSONEncoder)}\n\n"
                time.sleep(1)
            except Exception as e:
                app.logger.error(f"Error in SSE stream for conv {conversation_id}: {e}")
                # In a real app, you might want a mechanism to break the loop on certain errors.
                time.sleep(5) # Wait before retrying
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/api/conversation/<int:conversation_id>/message", methods=['POST'])
def api_post_message(conversation_id):
    try:
        user_prompt = request.json.get('prompt')
        parent_id = request.json.get('parent_id')
        if parent_id: db.deactivate_branch_from(parent_id)
        user_message_id = db.add_message(conversation_id, "user", user_prompt, parent_id)
        
        conv_settings = db.get_conversation(conversation_id)
        history = db.get_active_branch(conversation_id)
        messages = [{"role": "system", "content": conv_settings.system_prompt}]
        messages.extend([{"role": r.role, "content": r.content} for r in history])
        
        client = AIClient()
        model_handle = conv_settings.model

        # Use the streaming endpoint and accumulate the response
        full_response_text = ""
        response_stream = client.get_chat_response_stream(
            model_handle=model_handle,
            messages=messages,
            temperature=conv_settings.temperature,
            top_p=conv_settings.top_p
        )
        
        for chunk in response_stream:
            full_response_text += chunk.get("text", "")

        if full_response_text:
            db.add_message(conversation_id, "assistant", full_response_text, user_message_id)
        
        return jsonify({"success": True})
    except KlaiError as e:
        app.logger.error(f"Klai API Error in post_message for conv {conversation_id}: {e}")
        return jsonify(error=str(e)), 500

@app.route("/api/conversation/<int:conversation_id>/settings", methods=['POST'])
def api_update_settings(conversation_id):
    try:
        settings = request.json
        app.logger.info(f"Received settings update for conv #{conversation_id}: {settings}")

        temp_str = settings.get('temperature')
        top_p_str = settings.get('top_p')
        model = settings.get('model')
        title = settings.get('title')
        system_prompt = settings.get('system_prompt')

        # Gracefully handle empty strings for numeric fields
        temperature = float(temp_str) if temp_str and temp_str.strip() else None
        top_p = float(top_p_str) if top_p_str and top_p_str.strip() else None
        
        app.logger.info(f"Calling DB update for conv #{conversation_id} with: model='{model}', temp={temperature}, top_p={top_p}")

        db.update_conversation_settings(
            conversation_id,
            title,
            system_prompt,
            model,
            temperature,
            top_p
        )
        
        app.logger.info(f"Successfully updated settings for conv #{conversation_id}")
        return jsonify({"success": True, "message": "Settings saved successfully."})
    except Exception as e:
        app.logger.error(f"CRITICAL ERROR in api_update_settings for conv #{conversation_id}: {e}", exc_info=True)
        return jsonify(error=str(e)), 500

# --- Server Control ---
def run_server():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text())
            os.kill(pid, 0)
            return None
        except (OSError, ValueError):
            PID_FILE.unlink()
    env = os.environ.copy()
    env["FLASK_APP"] = "klai.web:app"
    
    # Use sys.executable to ensure we're using the python from the virtual env
    command = [sys.executable, "-m", "flask", "run", "--port", "5001"]
    
    process = subprocess.Popen(command, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
    with open(PID_FILE, "w") as f: f.write(str(process.pid))
    return process.pid

def stop_server():
    if not PID_FILE.exists(): return None
    with open(PID_FILE, "r") as f: pid = int(f.read())
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except ProcessLookupError: pass
    finally:
        if PID_FILE.exists(): PID_FILE.unlink()
    return pid

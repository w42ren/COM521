# save as app.py
from flask import Flask, request, make_response, jsonify
import uuid, hmac, hashlib, base64, time
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

# Server secret for HMAC signing (keep secret in real deployments)
SECRET_KEY = b"replace_this_with_a_strong_random_secret"

# Token TTL in seconds
TOKEN_TTL = 300  # 5 minutes

# In-memory store: session_id -> data
sessions = {}
# data example: {
#   "ip": "127.0.0.1",
#   "ua": "curl/7.x",
#   "last_seen": timestamp (float)
# }

def now_ts() -> float:
    return time.time()

def sign_token(raw: bytes) -> str:
    """Return base64(raw + '.' + signature)"""
    sig = hmac.new(SECRET_KEY, raw, hashlib.sha256).digest()
    payload = raw + b"." + sig
    return base64.urlsafe_b64encode(payload).decode("ascii")

def verify_token(token_b64: str):
    """Return (session_id, ts) if valid and not expired, otherwise (None,None)."""
    try:
        payload = base64.urlsafe_b64decode(token_b64.encode("ascii"))
        raw, sig = payload.rsplit(b".", 1)
        expected = hmac.new(SECRET_KEY, raw, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, sig):
            return None, None
        # raw format: session_id|ts
        parts = raw.split(b"|")
        if len(parts) != 2:
            return None, None
        session_id = parts[0].decode("ascii")
        ts = float(parts[1].decode("ascii"))
        if now_ts() - ts > TOKEN_TTL:
            return None, None
        return session_id, ts
    except Exception:
        return None, None

def make_token(session_id: str) -> str:
    raw = f"{session_id}|{now_ts()}".encode("ascii")
    return sign_token(raw)

@app.route("/issue")
def issue():
    """Issue a new session token and return it in header and body."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "ip": request.remote_addr,
        "ua": request.headers.get("User-Agent", ""),
        "last_seen": now_ts()
    }
    token = make_token(session_id)
    resp = make_response(jsonify({"session_id": session_id, "token": token}))
    # for demo we send token in a header (normally prefer secure HttpOnly cookie)
    resp.headers["X-Session-Token"] = token
    return resp

@app.route("/")
def protected():
    """A protected endpoint that validates tokens and detects suspicious reuse."""
    token = request.headers.get("X-Session-Token")
    if not token:
        return "Missing token", 401

    session_id, ts = verify_token(token)
    if not session_id:
        app.logger.warning("Invalid or expired token presented from %s UA=%s",
                           request.remote_addr, request.headers.get("User-Agent"))
        return "Invalid or expired token", 401

    data = sessions.get(session_id)
    if not data:
        app.logger.warning("Token for unknown session_id %s from %s", session_id, request.remote_addr)
        return "Unknown session", 401

    # Check for mismatch in fingerprint (IP or User-Agent)
    incoming_ip = request.remote_addr
    incoming_ua = request.headers.get("User-Agent", "")
    suspicious = False
    reasons = []
    if incoming_ip != data["ip"]:
        suspicious = True
        reasons.append(f"IP changed: {data['ip']} -> {incoming_ip}")
    if incoming_ua != data["ua"]:
        suspicious = True
        reasons.append(f"UA changed: {data['ua']} -> {incoming_ua}")

    # Update last seen if not suspicious, or still update but log
    sessions[session_id]["last_seen"] = now_ts()

    if suspicious:
        app.logger.warning("Suspicious session reuse detected for %s: %s", session_id, "; ".join(reasons))
        # Optionally: invalidate session to force re-login
        # del sessions[session_id]
        return jsonify({
            "status": "suspicious",
            "reasons": reasons
        }), 403

    # All good
    return jsonify({
        "status": "ok",
        "session_id": session_id,
        "issued_to_ip": data["ip"],
        "issued_to_ua": data["ua"]
    })

if __name__ == "__main__":
    # NOTE: run behind HTTPS in production!
    app.run(host="0.0.0.0", port=8080, debug=True)

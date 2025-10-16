from flask import Flask, request, make_response
import uuid

sample = Flask(__name__)

# Simple in-memory session store
sessions = {}

@sample.route("/")
def main():
    session_id = request.headers.get("Session-ID")

    if not session_id or session_id not in sessions:
        # New session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"ip": request.remote_addr}
        new_session = True
    else:
        new_session = False

    response_text = (
        f"Session ID: {session_id}\n"
        f"New Session: {new_session}\n"
        f"Your IP: {request.remote_addr}\n"
    )

    response = make_response(response_text)
    response.headers["Session-ID"] = session_id
    response.headers["Content-Type"] = "text/plain"
    return response

if __name__ == "__main__":
    sample.run(host="0.0.0.0", port=8080)

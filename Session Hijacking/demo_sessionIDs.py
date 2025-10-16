from flask import Flask, request, render_template, make_response
import uuid

sample = Flask(__name__)

@sample.route("/")
def main():
    # Check if the client sent a Session-ID header
    session_id = request.headers.get("Session-ID")
    
    if not session_id:
        # Generate a new session ID if none provided
        session_id = str(uuid.uuid4())
        new_session = True
    else:
        new_session = False

    # Prepare a simple response
    response_text = (
        f"Session ID: {session_id}\n"
        f"New Session: {new_session}\n"
        f"Your IP: {request.remote_addr}\n"
    )

    # Create a response object so we can add headers
    response = make_response(response_text)

    # Include the session ID in the response headers
    response.headers["Session-ID"] = session_id
    response.headers["Content-Type"] = "text/plain"

    return response

if __name__ == "__main__":
    sample.run(host="0.0.0.0", port=8080)

from flask import Flask, request, make_response, render_template, redirect, url_for, session
import uuid
# Create a Flask application instance
sample = Flask(__name__) 
sample.secret_key = "supersecretkey"  # Needed for session management
# Simple in-memory session store - type dictionary - to track sessions
sessions = {}

@sample.route("/")
def main():
    session_id = request.headers.get("Session-ID")
    print (sessions)
    if not session_id or session_id not in sessions:
# Generate a new session ID with a 128 bit Universally Unique Identifier UUID
        session_id = str(uuid.uuid4()) 
        sessions[session_id] = {"ip": request.remote_addr} # Store session data in memory with IP address as a key in the sessions dictionary 
        new_session = True
    else:
        new_session = False
# Prepare text for a simple response
    response_text = (   
        f"Session ID: {session_id}\n"
        f"New Session: {new_session}\n"
        f"Your IP: {request.remote_addr}\n"
    )

    response = make_response(response_text) # Create a response object so we can add headers
    response.headers["Session-ID"] = session_id # Include the session ID in the response headers
    response.headers["Content-Type"] = "text/plain" #   Set content type to plain text
    return response

@sample.route("/login", methods=["POST", "GET"])
def login():
     #   
    if request.method ==  "POST":
        user = request.form["username"]
        password = request.form["password"]
        session["user"] = user
 #       user = request.args.get("username")
 #       password = request.args.get("password")   
        if user == "admin" and password == "password":  # Simple authentication check
            session_id = str(uuid.uuid4())
            sessions[session_id] = {"ip": request.remote_addr, "user": user}
            response = make_response(f"Login successful. Session ID: {session_id}\n")
            response.headers["Session-ID"] = session_id
            response.headers["Content-Type"] = "text/plain"
            return response
        else:
            return "Invalid credentials\n", 401#
            # return redirect(url_for("user"))
    else:
        return render_template("login.html")
                              


@sample.route("/user")
def user():
    if response.headers["Session-ID"] in sessions :
        user = sessions["admin"]
        return f"<h1>Welcome {user}!</h1>"
    else:
        return redirect(url_for("login"))         


# Run the Flask app on all interfaces at port 8080
if __name__ == "__main__": 
    sample.run(host="0.0.0.0", port=8080) 

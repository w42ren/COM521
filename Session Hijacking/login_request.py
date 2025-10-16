import requests

# Target Flask app
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/login"

# Login credentials (same as in your Flask demo)
data = {
    "username": "admin",
    "password": "password"
}

# Create a session to persist cookies automatically
session = requests.Session()

# Perform POST login (like curl -X POST -d "username=admin&password=password")
response = session.post(LOGIN_URL, data=data)

# Print basic response info
print("Status Code:", response.status_code)
print("Response Text:\n", response.text)
print("-" * 50)

# Print cookies (automatically stored by requests.Session)
if session.cookies:
    print("Cookies stored in session:")
    for cookie in session.cookies:
        print(f"  {cookie.name} = {cookie.value}")
else:
    print("No cookies stored.")

print("-" * 50)

# Print headers (e.g., Session-ID header)
print("Response Headers:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

# Extract Session-ID header if present
session_id_header = response.headers.get("Session-ID")
if session_id_header:
    print("\nSession-ID (from header):", session_id_header)

# Now you can reuse the same session to call /user
user_url = f"{BASE_URL}/user"
user_response = session.get(user_url)
print("\n--- Accessing /user ---")
print("Status Code:", user_response.status_code)
print("Response Text:\n", user_response.text)

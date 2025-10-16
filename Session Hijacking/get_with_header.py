import requests

# Replace this with your actual Session ID value
session_id = "your_session_id_here"

# The target Flask server
url = "http://localhost:8080/"

# Set the custom header
headers = {
    "Session-ID": session_id
}

# Make the GET request
response = requests.get(url, headers=headers)

# Print the full response details
print("Status Code:", response.status_code)
print("Response Headers:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

print("\nResponse Body:\n", response.text)

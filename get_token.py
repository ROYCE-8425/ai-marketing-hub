"""Get GA4 OAuth2 refresh token."""
import http.server
import urllib.parse
import webbrowser
import json
import urllib.request
import os

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "YOUR_CLIENT_ID_HERE")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_CLIENT_SECRET_HERE")
REDIRECT_URI = "http://localhost:8888"
SCOPES = "https://www.googleapis.com/auth/analytics.readonly https://www.googleapis.com/auth/webmasters.readonly"

auth_code = None

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>OK! Quay lai terminal.</h1>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error")
    def log_message(self, *args): pass

# Step 1: Open browser for authorization
auth_url = (
    f"https://accounts.google.com/o/oauth2/v2/auth?"
    f"client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    f"&scope={urllib.parse.quote(SCOPES)}&access_type=offline&prompt=consent"
)
print("Opening browser for Google authorization...")
webbrowser.open(auth_url)

# Step 2: Wait for callback
server = http.server.HTTPServer(("localhost", 8888), Handler)
print("Waiting for authorization...")
while auth_code is None:
    server.handle_request()

print(f"Authorization code received!")

# Step 3: Exchange code for tokens
data = urllib.parse.urlencode({
    "code": auth_code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
}).encode()

req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
resp = urllib.request.urlopen(req)
tokens = json.loads(resp.read())

print("\n" + "=" * 60)
print("REFRESH TOKEN (save this!):")
print(tokens.get("refresh_token", "N/A"))
print("=" * 60)

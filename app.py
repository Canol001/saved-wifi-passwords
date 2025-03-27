import os
from flask import Flask, render_template
import subprocess

app = Flask(__name__)

def get_wifi_passwords():
    try:
        profiles_data = subprocess.run(
            ["netsh", "wlan", "show", "profiles"], 
            capture_output=True, text=True, encoding="utf-8"
        ).stdout

        if not profiles_data:
            return {}

        profiles = [line.split(":")[1].strip() for line in profiles_data.split("\n") if "All User Profile" in line]
        wifi_credentials = {}

        for profile in profiles:
            password_data = subprocess.run(
                ["netsh", "wlan", "show", "profile", profile, "key=clear"], 
                capture_output=True, text=True, encoding="utf-8"
            ).stdout

            password_lines = [line.split(":")[1].strip() for line in password_data.split("\n") if "Key Content" in line]
            wifi_credentials[profile] = password_lines[0] if password_lines else "No password set"

        return wifi_credentials

    except Exception as e:
        return {"Error": str(e)}

@app.route("/")
def index():
    wifi_info = get_wifi_passwords()
    return render_template("index.html", wifi_info=wifi_info)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's dynamic port
    app.run(host="0.0.0.0", port=port, debug=False)

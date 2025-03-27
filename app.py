import os
import platform
import subprocess
from flask import Flask, render_template

app = Flask(__name__)

def get_wifi_passwords():
    wifi_credentials = {}

    if platform.system() == "Windows":
        try:
            profiles_data = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True, text=True, encoding="utf-8"
            ).stdout

            profiles = [line.split(":")[1].strip() for line in profiles_data.split("\n") if "All User Profile" in line]

            for profile in profiles:
                password_data = subprocess.run(
                    ["netsh", "wlan", "show", "profile", profile, "key=clear"],
                    capture_output=True, text=True, encoding="utf-8"
                ).stdout

                password_lines = [line.split(":")[1].strip() for line in password_data.split("\n") if "Key Content" in line]
                wifi_credentials[profile] = password_lines[0] if password_lines else "No password set"

        except Exception as e:
            wifi_credentials["Error"] = str(e)

    elif platform.system() == "Linux":
        try:
            profiles_data = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SECURITY", "dev", "wifi"],
                capture_output=True, text=True, encoding="utf-8"
            ).stdout

            profiles = profiles_data.strip().split("\n")
            for profile in profiles:
                ssid, security = profile.split(":")
                wifi_credentials[ssid] = security

        except Exception as e:
            wifi_credentials["Error"] = str(e)

    else:
        wifi_credentials["Error"] = "Unsupported OS"

    return wifi_credentials

@app.route("/")
def index():
    wifi_info = get_wifi_passwords()
    return render_template("index.html", wifi_info=wifi_info)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

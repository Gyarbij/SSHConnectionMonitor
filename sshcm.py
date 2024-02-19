import os
import time
import re
import subprocess

def check_ssh_connections(last_line):
    log_files = ['/var/log/auth.log', '/var/log/secure']  # Add other log files if needed
    new_last_line = last_line

    for log_file in log_files:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()

            if not lines:
                continue

            new_last_line = lines[-1]

            if last_line:
                lines = lines[lines.index(last_line) + 1:]
            
            for line in lines:
                if 'sshd' in line:
                    if 'Accepted' in line:
                        match = re.search(r'Accepted .* for (.*?) from (.*?) port', line)
                        if match:
                            user, ip = match.groups()
                            send_alert(f"A new SSH connection (accepted publickey) from {user}@{ip}!", "SSH Alert")

                    elif 'Failed password' in line:
                        match = re.search(r'Failed password for (.*?) from (.*?) port', line)
                        if match:
                            user, ip = match.groups()
                            send_alert(f"Failed SSH login attempt (wrong password) detected from {user}@{ip}!", "SSH Warning")

                    elif 'Invalid user' in line:
                        match = re.search(r'Invalid user (.*?) from (.*?) port', line)
                        if match:
                            user, ip = match.groups()
                            send_alert(f"Failed SSH login attempt (invalid user) detected for {user}@{ip}!", "SSH Warning")

                    # Handle failed key authentication case
                    elif 'Failed publickey' in line or 'Connection closed by authenticating user' in line:
                        match = re.search(r'for (.*?) from (.*?) port', line)
                        if match:
                            user, ip = match.groups()
                            send_alert(f"Failed SSH login attempt (incorrect key file) detected for {user}@{ip}!", "SSH Warning")

    return new_last_line

def send_alert(message, title):
    print(message)
    if is_gui_session():
        send_desktop_notification(message, title)

def is_gui_session():
    """Check if the current session is a GUI session"""
    return os.environ.get("DISPLAY") is not None

def send_desktop_notification(message, title):
    """Send a desktop notification"""
    try:
        subprocess.run(['notify-send', title, message], check=True)
    except Exception as e:
        print(f"Failed to send desktop notification: {e}")

def main():
    last_line = None
    
    while True:
        last_line = check_ssh_connections(last_line)
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()
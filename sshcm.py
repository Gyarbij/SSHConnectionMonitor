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
                if 'sshd' in line and 'Accepted' in line:
                    match = re.search(r'Accepted .* for (.*?) from (.*?) port', line)
                    if match:
                        user, ip = match.groups()
                        send_alert(user, ip)

    return new_last_line

def send_alert(user, ip):
    message = f"Alert: A new SSH connection has been detected from {user}@{ip}!"
    print(message)
    if is_gui_session():
        send_desktop_notification(message)

def is_gui_session():
    """Check if the current session is a GUI session"""
    return os.environ.get("DISPLAY") is not None

def send_desktop_notification(message):
    """Send a desktop notification"""
    try:
        subprocess.run(['notify-send', 'SSH Alert', message], check=True)
    except Exception as e:
        print(f"Failed to send desktop notification: {e}")

def main():
    last_line = None
    
    while True:
        last_line = check_ssh_connections(last_line)
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()

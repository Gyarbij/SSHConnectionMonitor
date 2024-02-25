#!/usr/bin/env python
import argparse
import datetime
import logging
import os
import re
import subprocess
import sys
import time

try:
    from systemd import journal
except ImportError:
    print("No journal monitoring available. Install python-systemd", file=sys.stderr)


parser = argparse.ArgumentParser(description='Alert when someone logs in via SSH')

parser.add_argument(
    "-d",
    "--debug",
    action="store_true",
    help="increase output verbosity and log temp files",
)

parser.add_argument(
    "--monitor",
    choices=["files", "journald"],
    help="Select which source to monitor for ssh logins",
)

args = parser.parse_args()

log = logging.getLogger('ssh_notifier')
log.setLevel("DEBUG" if args.debug else "INFO")


def search_for_message(line: str):
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


def send_desktop_notification(message: str, title: str):
    """Send a desktop notification"""
    log.debug("Sending '{message}' to dbus notification")
    try:
        subprocess.run(['notify-send', '--urgency', 'critical', title, message], check=True)
    except Exception as e:
        log.error(f"Failed to send desktop notification: {e}")


def send_alert(message: str, title: str):
    log.info(message)
    if is_gui_session():
        send_desktop_notification(message, title)


def is_gui_session() -> bool:
    """Check if the current session is a GUI session"""
    return os.environ.get("DISPLAY") is not None or \
        os.environ.get("WAYLAND_DISPLAY") is not None


def monitor_journal():
    j = journal.Reader()
    j.this_boot()
    j.log_level(journal.LOG_INFO)
    j.add_match(SYSLOG_IDENTIFIER="sshd")
    j.seek_realtime(datetime.datetime.now())

    while True:
        response = j.wait()
        log.debug(f"Finished waiting. State: {response}")
        for entry in j:
            log.debug(entry['MESSAGE'])
            search_for_message(entry['MESSAGE'])

        log.debug("Finished processing")


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
                    search_for_message(line)
    return new_last_line


def main():

    match args.monitor:
        case "files":
            last_line = None

            while True:
                last_line = check_ssh_connections(last_line)
                time.sleep(10)  # Check every 10 seconds
        case "journald":
            monitor_journal()
        case _:
            log.error("Monitoring argument must be provided")
            exit(-1)


if __name__ == "__main__":
    main()

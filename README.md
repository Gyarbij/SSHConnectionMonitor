# SSHConnectionMonitor
Alert signed in user in terminal if a new ssh connection is initiated.

## Description

This script checks the auth.log and secure log files for SSH connections and prints an alert message to the terminal whenever a new connection is detected. It also includes the username and IP address in the alert message.

## Prerequisites

- Python 3 installed on your Linux server.
- Root access to the server, as the script needs to read system log files.

## Installation

1. Open a terminal.
2. Clone this repository to your local machine using the following command: 'git clone https://github.com/Gyarbij/SSHConnectionMonitor.git'
3. Navigate to the cloned repository: 'cd SSHConnectionMonitor'

## Usage

1. Run the script with Python 3: 'sudo python3 sshcm.py &' The `&` at the end of the command will run the script in the background, allowing you to continue using the terminal for other tasks.

2. To check if the script is running, you can use the `jobs` command. You should see the `sshcm.py` script listed.

3. The script will start monitoring the log files for new SSH connections. When a new connection is detected, it will print an alert message to the terminal.

4. If you want to stop the script, you can use the `fg` command to bring it to the foreground and then press `Ctrl+C` to stop it.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

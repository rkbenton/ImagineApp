# Raspberry Pi Deploy

### Setting up Raspberry Pi 5:

# Overview

- Add necessary credentials for git, aws, OpenAI
- Clone the repository
  - create .venv
  - update pip
  - install dependencies
  - set up `.env` with IM_IM_XXXX paths
- Manual test of the app
- Create systemd service to auto-run the app via gunicorn
- Configure journalctl logging


#### Update everything, all the time, always
https://www.raspberrypi.com/documentation/computers/os.html#update-software
```
sudo apt-get update -y
sudo apt full-upgrade -y
sudo apt dist-upgrade -y
sudo rpi-update
sudo reboot
```

#### Setting up SSH for GitHub
On your Mac:
Check if you have an rsa key already:
```
ls -lha ~/.ssh/id_rsa*
```
If not:
- Run `ssh-keygen -t rsa`
- `ssh-keygen -t rsa -b 4096 -C "becky@beckybenton.com"`
- passphrase: **read more books**

you should get back something like:
```
Your identification has been saved in /home/becky/.ssh/id_rsa
Your public key has been saved in /home/becky/.ssh/id_rsa.pub
```
Add the SSH Key to Your GitHub Account:

```
cat ~/.ssh/id_rsa.pub
```
- Go to GitHub and log in to your account.
- In the upper-right corner of any page, click your profile photo, then click Settings.
- In the user settings sidebar, click SSH and GPG keys.
- Click New SSH key or Add SSH key.
- In the "Title" field, add a descriptive label for the new key.
- Paste your key into the "Key" field.
- Click Add SSH key.

Test the SSH Connection:

```
ssh -T git@github.com
```
You should see a successful communication with GH!

# Clone the Repo
```
cd ~
git clone git@github.com:rkbenton/ImagineApp.git
cd ImagineApp
ls -lha
```

### Create Python .venv and pull in dependencies

```bash
cd ~/ImagineApp
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
and the .env:
```
nano .env
```
then, paste in the contents of your current .env file.

# Manually run gunicorn server
Let's say the Raspi's hostname is "irving". You should be able to fire up the gunicorn server:
```
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```
and then hit our little web app from, say, your MacBook:
```
http://irving.local:5001
```
Presumably that works, but test it out a bit. You'll want to kill the server
once you're satisfied.

# Add a systemd service

But first, where is gunicorn?
```bash
whereis gunicorn
```
I got back `gunicorn: /home/becky/ImagineApp/.venv/bin/gunicorn`

```
sudo nano /etc/systemd/system/imagineapp.service
```
and stick in the following:
```
[Unit]
Description=ImagineApp Gunicorn Server
After=network.target
# Prevent excessive restarts
# Defines a 5-minute (300 seconds) window for tracking restarts
StartLimitIntervalSec=300
# Allows up to 5 restarts within the 5-minute window before disabling further attempts
StartLimitBurst=5

[Service]
Type=simple
User=becky
WorkingDirectory=/home/becky/ImagineApp
ExecStart=/home/becky/ImagineApp/.venv/bin/gunicorn -w 2 -b 0.0.0.0:5001 app:app
Restart=always
# Waits n seconds before restarting to avoid excessive quick restarts
RestartSec=15s

# disabling output buffering forces Python to print everything immediately
Environment="PYTHONUNBUFFERED=1"

# Ensure clean exit
# Sends SIGINT instead of SIGTERM to allow graceful shutdown
KillSignal=SIGINT
# Waits up to 20 seconds for the process to stop before forcefully killing it
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable imagineapp
sudo systemctl start imagineapp
```
You should be able to hit the endpoint now:
```bash
http://<hostname.local>:5001/
```


# Managing the ImagineImage Startup Service

Enable and start the service:
```
sudo systemctl stop imagineapp.service
sudo systemctl daemon-reload
sudo systemctl enable imagineapp.service
sudo systemctl start imagineapp.service
```

Check the status:
```
sudo systemctl status imagineapp.service
```

Useful commands for managing the service:

- Stop: `sudo systemctl stop imagineapp.service`
- Restart: `sudo systemctl restart imagineapp.service`
- View logs: `journalctl -u imagineapp.service`
- View only last 10 mins of log

 ```
journalctl -u imagineapp.service --no-pager --since "10 minutes ago"
journalctl -u imagineapp.service --no-pager --since "5 minutes ago"
journalctl -u imagineapp.service --no-pager --since "30 seconds ago"
```
# Prevent logging from choking the disk
Our print statements go to the system-maintained logs managed by journalctl. The default journalctl logs can grow and consume disk space. Here's how to manage it:

Check current disk usage:
```
journalctl --disk-usage
```

View current settings:
```
sudo journalctl --vacuum-size=1G
sudo journalctl --vacuum-time=1weeks
```

You can set persistent limits by editing the journal configuration:
```
sudo nano /etc/systemd/journald.conf
```

Add or modify these lines:
```
SystemMaxUse=1G
SystemMaxFileSize=100M
MaxRetentionSec=1week
```

Then restart the journal service:
```
sudo systemctl restart systemd-journald
```
Common settings:

- SystemMaxUse: Maximum disk space used
- MaxRetentionSec: How long to keep logs
- SystemMaxFileSize: Maximum size per file

For a Raspberry Pi, you might want to use smaller values like:
```
SystemMaxUse=100M
MaxRetentionSec=3days
```

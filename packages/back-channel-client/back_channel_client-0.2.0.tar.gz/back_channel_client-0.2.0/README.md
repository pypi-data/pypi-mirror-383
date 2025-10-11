![PyPI - Version](https://img.shields.io/pypi/v/rpi-remote?style=for-the-badge&logo=python&logoColor=yellow&link=https%3A%2F%2Fpypi.org%2Fproject%2Frpi-remote%2F)

# Back Channel client

## Installation

### Install/Upgrade package
``` shell
python3 -m pip install --upgrade back-channel-client --user
```

### Create service
``` shell
echo "[Unit]
Description=back-channel-client
After=multi-user.target
Conflicts=getty@tty1.service
[Service]
User=${USER}
Type=simple
Environment="LC_ALL=C.UTF-8"
Environment="LANG=C.UTF-8"
ExecStart=${HOME}/.local/bin/back-channel-client
Restart=on-failure
RestartSec=3
[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/back-channel-client.service
```
``` shell
sudo systemctl daemon-reload
sudo systemctl enable back-channel-client.service
sudo systemctl start back-channel-client.service
```

## Configuration
Config file path: ```~/.config/back_channel_client/config.ini```

This file automatically generated when the service starts. See the example below.
``` ini
[connection]
server_host = http://localhost
ssh_username = root
ssh_port = 22
period_time_sec = 30
client_name = test_client
disk_path = /media/HDD
```

## Check logs
``` shell
journalctl -fu back-channel-client
```

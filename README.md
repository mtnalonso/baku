# Baku

Baku is a minimal sftp backup manager that can be configured to perform multiple backups of different files across many hosts.

## Installation
An installation script is provided in order to setup a Raspberry pi as a minimal backup server.

```bash
chmod +x setup.sh
./setup.sh
```

If you have Python already installed on your system, the only requirements needed is the library `pysftp`, which can be installed with pip.
```bash
pip3 install pysftp
```

## Configuration
The `config.py` file stores the configuration of the different backup files and hosts. This file can be easily created by copying the `config.dist.py` file.

```python
DESTINATION_FOLDER = ''                     # Destination path to store the files
DEFAULT_DAILY_LIMIT = 14                    # Default daily backups to store
DEFAULT_WEEKLY_LIMIT = 6                    # Default weekly backups to store
DEFAULT_MONTHLY_LIMIT = 12                  # Default of monthly backups to store


hosts = {
    'HOSTNAME-A': {
        'ip': 'X.X.X.X',
        'username': 'BACKUP_USERNAME',
        'private_key': '/path/to/file',
        'private_key_pass': 'PRIVATE_KEY_PASSWORD',
    },
}


backups = [
    {
        'name': 'Name of this backup',
        'hostname': 'HOSTNAME',             # Hostname key from hosts configuration
        'location': '/your/host/file',      # Source path of the file
        'destination': 'my_backup/',        # Destination path inside the DESTINATION_FOLDER
        'daily_limit': '14',                # Custom daily backups to store
        'weekly_limit': '',                 # Custom weekly backups to store
    }
]
```


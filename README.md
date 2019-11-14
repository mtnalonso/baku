# Baku

Baku is a minimal sftp backup manager that can be configured to perform multiple backups of different files across many hosts.


### Config file
The `config.py` file stores the configuration of the different backup files and hosts. This file can be easily created by copying the `config.dist.py` file.

```python
DESTINATION_FOLDER = ''                     # Destination path to store the files
DEFAULT_DAILY_LIMIT = 14                    # Default daily backups to store
DEFAULT_WEEKLY_LIMIT = 6                    # Default weekly backups to store
DEFAULT_MONTHLY_LIMIT = 12                  # Default of monthly backups to store


hosts = {
    'HOSTNAME': {
        'ip': 'X.X.X.X',
        'username': 'BACKUP_USERNAME',
        'password': 'BACKUP_PASSWORD',
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


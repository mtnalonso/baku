from datetime import datetime
import argparse
import glob
import os
import shutil

import pysftp

import config


if config.DESTINATION_FOLDER:
    BAKU_DEST_PATH = config.DESTINATION_FOLDER
else:
    BAKU_DEST_PATH = '{}/backups'.format(os.getcwd())

LAST_BACKUP_FILENAME = 'last'


def load_args():
    parser = argparse.ArgumentParser(prog='baku.py')
    parser.add_argument('-c', '--cron', action='store_true')
    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('-s', '--sync', action='store_true')
    return parser.parse_args()


def run_backups(hosts_config, backups_config):
    for backup in backups_config:
        source_host = hosts_config[backup['hostname']]
        user = source_host.get('username')
        password = source_host.get('password')
        ip = source_host.get('ip')
        private_key = source_host.get('private_key')
        private_pass = source_host.get('private_key_pass')
        # TODO if host has custom port

        get_backup_file(ip, user, password, backup, private_key, private_pass)
    return


def get_backup_file(ip, user, password, backup_file_details, private_key=None,
                    private_pass=None):
    destination_path = '{}/{}'.format(
            BAKU_DEST_PATH,
            backup_file_details['destination']
    )
    prepare_destination_folder(destination_path)

    filename = backup_file_details['filename']
    remote_location = backup_file_details['location']
    backup_file_extension = filename.split('.', maxsplit=1)[-1]
    backup_date = datetime.now().strftime("%Y-%m-%d")
    # TODO: remove daily from filename

    dest_file = '{}daily-{}.{}'.format(
        destination_path, backup_date, backup_file_extension
    )

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    
    if private_key:
        with pysftp.Connection(
            ip, username=user, private_key=private_key,
            private_key_pass=private_pass, cnopts=cnopts
        ) as sftp:
            with sftp.cd(remote_location):
                print('[*] Downloading {}...'.format(
                    backup_file_details.get('name', '')
                ))
                sftp.get(filename, localpath=dest_file)
                print('[+] Downloaded {}'.format(
                    backup_file_details.get('name', '')
                ))
    else:
        with pysftp.Connection(
            ip, username=user, password=password, cnopts=cnopts
        ) as sftp:
            with sftp.cd(backup_file_details['location']):
                print('[*] Downloading {}...'.format(
                    backup_file_details.get('name', '')
                ))
                sftp.get(backup_file_details['filename'], localpath=dest_file)
                print('[+] Downloaded {}'.format(
                    backup_file_details.get('name', '')
                ))

    copy_file_as_last_backup(dest_file, destination_path, config.DEFAULT_LAST_FILENAME)
    return


def prepare_destination_folder(destination_path):
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    return


def copy_file_as_last_backup(file_to_copy, dest_path, default_last_filename):
    file_extension = file_to_copy.split('.', 1)[1]
    default_last_filename += '.' + file_extension
    shutil.copy2(file_to_copy, dest_path + default_last_filename)
    return

def validate_backup_file(backups_config):
    # TODO: this function will call a validator to check the file integrity
    pass


def reorder_backup_files(backups_config):
    today = datetime.today()
    for backup_info in backups_config:
        reorder_yearly_backup_files(today, backup_info)
        reorder_monthly_backup_files(today, backup_info)
        reorder_weekly_backup_files(today, backup_info)
        reorder_daily_backup_files(today, backup_info)
    return


def reorder_yearly_backup_files(today, backup_info):
    current_day_of_year = today.timetuple().tm_yday

    file_extension = '.' + backup_info['filename'].split('.', 1)[1]
    dest_path = BAKU_DEST_PATH + '/' + backup_info['destination']

    if current_day_of_year == 1:
        yearly_filename = 'yearly-{}{}'.format(
            str(today.date()), file_extension
        )
        print('creating {}'.format(yearly_filename))
        shutil.copy2(
            dest_path + config.DEFAULT_LAST_FILENAME + file_extension,
            dest_path + yearly_filename
        )
    return 


def reorder_monthly_backup_files(today, backup_info):
    current_day_of_month = today.day

    file_extension = '.' + backup_info['filename'].split('.', 1)[1]
    dest_path = BAKU_DEST_PATH + '/' + backup_info['destination']

    if current_day_of_month == 1:
        # TODO: check if file already exists
        monthly_filename = 'monthly-{}{}'.format(
            str(today.date()), file_extension
        )
        print('creating {}'.format(monthly_filename))
        shutil.copy2(
            dest_path + config.DEFAULT_LAST_FILENAME + file_extension,
            dest_path + monthly_filename
        )
    return 


def reorder_weekly_backup_files(today, backup_info):
    current_day_of_week = today.isoweekday()

    file_extension = '.' + backup_info['filename'].split('.', 1)[1]
    dest_path = BAKU_DEST_PATH + '/' + backup_info['destination']

    if current_day_of_week == 1:
        # TODO: check if file already exists
        weekly_filename = 'weekly-{}{}'.format(
            str(today.date()), file_extension
        )
        print('creating {}'.format(weekly_filename))
        shutil.copy2(
            dest_path + config.DEFAULT_LAST_FILENAME + file_extension,
            dest_path + weekly_filename
        )
    return


def reorder_daily_backup_files(today, backup_info):
    backup_dir = BAKU_DEST_PATH + '/' + backup_info.get('destination')
    daily_files = glob.glob(backup_dir + 'daily*')
    default_max_files = config.DEFAULT_DAILY_LIMIT
    max_daily_files = int(backup_info.get('daily_limit', default_max_files))

    while len(daily_files) > max_daily_files:
        oldest_backup = min(daily_files, key=os.path.getctime)
        print('removing {}'.format(oldest_backup))
        os.remove(oldest_backup)
        daily_files = glob.glob(backup_dir + 'daily*')
    return


if __name__ == '__main__':
    args = load_args()

    if args.cron:
        run_backups(config.hosts, config.backups)
        validate_backup_file(config.backups)
        reorder_backup_files(config.backups)
    elif args.sync:
        reorder_backup_files(config.backups)
    elif args.force:
        raise NotImplementedError('Forced backup not implemented yet')

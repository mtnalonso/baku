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

LAST_BACKUP_FILENAME = 'last.sql.gz'


hosts = config.hosts
backups = config.backups


def load_args():
    parser = argparse.ArgumentParser(prog='baku.py')
    parser.add_argument('-c', '--cron', action='store_true')
    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('-s', '--sync', action='store_true')
    return parser.parse_args()


def new_runner():
    for backup in backups:
        source_host = hosts[backup['hostname']]
        user = source_host['username']
        password = source_host['password']
        ip = source_host['ip']
        # TODO if host has custom port

        get_backup_file(ip, user, password, backup)
    return


def get_backup_file(ip, user, password, backup_file_details):
    destination_path = '{}/{}'.format(
            BAKU_DEST_PATH,
            backup_file_details['destination']
    )
    prepare_destination_folder(destination_path)

    backup_date = datetime.now().strftime("%Y-%m-%d")
    # TODO: remove daily from filename
    dest_file = '{}daily-{}.sql.gz'.format(destination_path, backup_date)

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(ip, username=user, password=password, cnopts=cnopts) as sftp:
        with sftp.cd(backup_file_details['location']):
            print('[*] Downloading {}...'.format(backup_file_details.get('name', '')))
            sftp.get(backup_file_details['filename'], localpath=dest_file)
            print('[+] Downloaded {}'.format(backup_file_details.get('name', '')))

    copy_file_as_last_backup(dest_file, destination_path, config.DEFAULT_LAST_FILENAME)
    return


def prepare_destination_folder(destination_path):
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    return


def copy_file_as_last_backup(file_to_copy, dest_path, default_last_filename):
    shutil.copy2(file_to_copy, dest_path + default_last_filename)
    return


def run_cron_task():
    user = creds.USERNAME
    password = creds.PASSWORD
    host = creds.HOST
    directory = creds.PATH
    filename = creds.FILENAME

    backup_date = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(DEST_PATH):
        os.makedirs(DEST_PATH)

    dest_path = '{}daily-{}.sql.gz'.format(DEST_PATH, backup_date)

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(host, username=user, password=password, cnopts=cnopts) as sftp:
        with sftp.cd(directory):
            print('[*] Downloading {}...'.format(filename))
            sftp.get(filename, localpath=dest_path)
            print('[+] Downloaded {}'.format(filename))

    shutil.copy2(dest_path, DEST_PATH + LAST_BACKUP_FILENAME)
    return


def validate_backup_file():
    # TODO: this function will call a validator to check the file integrity
    pass


def reorder_backup_files():
    today = datetime.today()
    reorder_yearly_backup_files(today)
    reorder_monthly_backup_files(today)
    reorder_weekly_backup_files(today)
    reorder_daily_backup_files(today)


def reorder_yearly_backup_files(today):
    current_day_of_year = today.timetuple().tm_yday
    if current_day_of_year == 1:
        yearly_filename = 'yearly-{}.sql.gz'.format(str(today.date()))
        print('creating {}'.format(yearly_filename))
        shutil.copy2(
            DEST_PATH + LAST_BACKUP_FILENAME, DEST_PATH + yearly_filename
        )
    return 


def reorder_monthly_backup_files(today):
    current_day_of_month = today.day
    if current_day_of_month == 1:
        # TODO: check if file already exists
        monthly_filename = 'monthly-{}.sql.gz'.format(str(today.date()))
        print('creating {}'.format(monthly_filename))
        shutil.copy2(
            DEST_PATH + LAST_BACKUP_FILENAME, DEST_PATH + monthly_filename
        )
    return 


def reorder_weekly_backup_files(today):
    current_day_of_week = today.isoweekday()
    if current_day_of_week == 1:
        # TODO: check if file already exists
        weekly_filename = 'weekly-{}.sql.gz'.format(str(today.date()))
        print('creating {}'.format(weekly_filename))
        shutil.copy2(
            DEST_PATH + LAST_BACKUP_FILENAME, DEST_PATH + weekly_filename
        )
    return


def reorder_daily_backup_files(today):
    daily_files = glob.glob(DEST_PATH + 'daily*')
    while len(daily_files) > 14:
        oldest_backup = min(daily_files, key=os.path.getctime)
        print('removing {}'.format(oldest_backup))
        os.remove(oldest_backup)
        daily_files = glob.glob(DEST_PATH + 'daily*')
    return


if __name__ == '__main__':
    args = load_args()

    if args.cron:
        run_cron_task()
        validate_backup_file()
        reorder_backup_files()
    elif args.sync:
        reorder_backup_files()
    elif args.force:
        new_runner()
        raise NotImplementedError('Forced backup not implemented yet')

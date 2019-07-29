import argparse
from datetime import datetime
import os
import shutil

import pysftp

import creds


DEST_PATH = '{}/{}'.format(os.getcwd(), creds.DEST_PATH)
LAST_BACKUP_FILENAME = 'last.tar.gz'


def load_args():
    parser = argparse.ArgumentParser(prog='baku.py')
    parser.add_argument('-c', '--cron', action='store_true')
    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('-s', '--sync', action='store_true')
    return parser.parse_args()


def run_cron_task():
    user = creds.USERNAME
    password = creds.PASSWORD
    host = creds.HOST
    directory = creds.PATH
    filename = creds.FILENAME

    backup_date = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    dest_path = '{}{}_{}'.format(DEST_PATH, backup_date, filename)

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
        yearly_filename = 'yearly-{}.tar.gz'.format(today.year)
        print('creating {}'.format(yearly_filename))
        shutil.copy2(DEST_PATH + LAST_BACKUP_FILENAME, yearly_filename)
    return 


def reorder_monthly_backup_files(today):
    current_day_of_month = today.day
    if current_day_of_month == 1:
        monthly_filename = 'monthly-{}.tar.gz'.format(today.month)
        print('creating {}'.format(monthly_filename))
        shutil.copy2(DEST_PATH + LAST_BACKUP_FILENAME, monthly_filename)
    return 


def reorder_weekly_backup_files(today):
    current_day_of_week = today.isoweekday()
    if current_day_of_week == 1:
        weekly_filename = 'weekly-{}.tar.gz'.format(str(today.date()))
        print('creating {}'.format(weekly_filename))
        shutil.copy2(DEST_PATH + LAST_BACKUP_FILENAME, weekly_filename)
    return


def reorder_daily_backup_files(today):
    daily_files = os.listdir(DEST_PATH + 'daily*')
    if len(daily_files) > 14:
        oldest_backup = min(daily_files, key=os.path.getctime)
        print('removing {}{}'.format(DEST_PATH, oldest_backup))
        os.remove(DEST_PATH + oldest_backup)
    return


if __name__ == '__main__':
    args = load_args()

    if args.cron:
        run_cron_task()
        reorder_backup_files()
    elif args.sync:
        reorder_backup_files()
    elif args.force:
        raise NotImplementedError('Forced backup not implemented yet')

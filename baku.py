import argparse
import datetime
import os

import pysftp

import creds


def load_args():
    parser = argparse.ArgumentParser(prog='baku.py')
    parser.add_argument('-c', '--cron', action='store_true')
    return parser.parse_args()


def run_cron_task():
    user = creds.USERNAME
    password = creds.PASSWORD
    host = creds.HOST
    directory = creds.PATH
    filename = creds.FILENAME
    dest_path = creds.DEST_PATH

    backup_date = datetime.datetime.now().strftime("%Y-%m-%d")
    dest_path = '{}/{}'.format(os.getcwd(), dest_path)

    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    dest_path = '{}{}_{}'.format(dest_path, backup_date, filename)

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(host, username=user, password=password, cnopts=cnopts) as sftp:
        with sftp.cd(directory):
            print('[*] Downloading {}...'.format(filename))
            sftp.get(filename, localpath=dest_path)
            print('[+] Downloaded {}'.format(filename))
    return


if __name__ == '__main__':
    args = load_args()

    if args.cron:
        run_cron_task()

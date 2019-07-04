import creds
import pysftp


if __name__ == '__main__':
    user = creds.USERNAME
    password = creds.PASSWORD
    host = creds.HOST
    directory = creds.PATH
    filename = creds.FILENAME

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(host, username=user, password=password, cnopts=cnopts) as sftp:
        with sftp.cd(directory):
            print('[*] Downloading {}...'.format(filename))
            sftp.get(filename)
            print('[+] Downloaded {}'.format(filename))

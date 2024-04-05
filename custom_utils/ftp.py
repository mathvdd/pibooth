import pysftp
from json import load as jsonload
import os

class ftp():

    def ftp_disconnect(self):
        if self.connection is not None:
            self.connection.close()
            print(f"Disconnected from ftp")

    def ftp_connection(self):
        print('Connecting to ftp')
        self.ftp_cred()
        try:
            # Get the sftp connection object
            self.connection = pysftp.Connection(
                host=self.ftpcred['host'],
                username=self.ftpcred['user'],
                password=self.ftpcred['pwd'],
                port=22,
            )
            print(f"Connected to ftp.")
        except:
            self.connection = None
            print(f"Failed to connect to ftp.")

    def try_connected(self):
        if self.connection is not None:
            return True
        else:
            self.ftp_connection()
        if self.connection is not None:
            return True
        else:
            return False


    def ftp_listdir(self, remote_path):
        if self.try_connected():
            try:
                self.connection.stat(remote_path)  # Test if remote_path exists
                dirs = self.connection.listdir(remote_path)

            except IOError:
                print(f'Could not check content of {remote_path} because it does not exists')
                dirs = []

            return dirs

    def ftp_download(self,dist,local):
        if self.try_connected():
            try:
                print(f"Downloading {dist}")
                # Download from remote sftp server to local
                self.connection.get(dist, local)
                print(f"Downloaded {dist} to {local}")
            except:
                print(f"Could not download {dist} to {local}")

    def ftp_upload(self, local, dist):
        if self.try_connected():
            try:
                #first check if the folder exists
                try:
                    self.connection.stat(os.path.split(dist)[0])  # Test if remote_path exists
                except IOError:
                    self.connection.mkdir(os.path.split(dist)[0])  # Create remote_path

                #upload
                print(f"Uploading {local}")
                self.connection.put(local, dist)
                print(f"Uploaded {local} to {dist}")
            except:
                print(f"Could not upload {local} to {dist}")

    def ftp_cred(self):
        with open('/opt/pibooth/custom_utils/.ftpcred.json') as json_file:
            self.ftpcred = jsonload(json_file)

if __name__=='__main__':
    ftp = ftp()
    ftp.path_ftpcred = '.ftpcred.json'
    ftp.ftp_connection()
    dirs=ftp.ftp_listdir('www/pibooth')
    print(dirs)
    ftp.ftp_disconnect()

import os
import urllib.request
import shutil
from json import load as jsonload
import time
from base64 import b64decode as dec
from urllib import request
import ftp

class iobj():

    def __init__(self, ftp_on=True):

        self.path_cfg_local = os.path.join(os.path.expanduser('~'), '.config/pibooth/pibooth.cfg')
        self.path_cfg_web = os.path.join(os.path.expanduser('~'), '.config/pibooth/conf_web.json')
        self.cfg_fromjson = None

        if os.path.isdir('/USB/im'):
            self.path_im_local_root = '/USB/im/'
        else:
            print('Could not find local image root /USB/im/')
            self.path_im_local_root = os.path.join(os.path.expanduser('~'), 'Pictures/pibooth/')

        if ftp_on:
            self.ftp = ftp.ftp()
            self.ftp.ftp_connection()


    def fetch_cfg_from_web(self):
        try:
            print(os.path.join(self.ftp.ftpcred["path_web"],
                                    'admin', f'conf_web_{self.ftp.ftpcred["boothname"]}.json'))
            self.ftp.ftp_download(os.path.join(self.ftp.ftpcred["path_web"],
                                    'admin', f'conf_web_{self.ftp.ftpcred["boothname"]}.json'),
                                self.path_cfg_web)
            print('Fichier de configuration téléchargé depuis le web')
        except:
            print('Echec de téléchargement du fichier de configuration')

    def update_cfg_from_json(self):
        self.fetch_cfg_from_web()
        print('Updating config from json file')
        #open local file
        if os.path.isfile(self.path_cfg_web):
            with open(self.path_cfg_web) as json_file:
                self.cfg_fromjson = jsonload(json_file)

            print(f'Setting envent to {self.get_event_folder()}')

            with open(self.path_cfg_local,'r') as f:
                get_all=f.readlines()

            with open(self.path_cfg_local,'w') as f:
                for line in get_all:
                    confkey = line.split("=")[0].strip()
                    if confkey in self.cfg_fromjson.keys():
                        f.writelines(f'{confkey} = {self.cfg_fromjson[confkey]}\n')
                    else:
                        f.writelines(line)
        else:
            print('Could not find conf_web.json (from update cfg function)')

    def get_event_folder(self):
        if self.cfg_fromjson is None:
            if os.path.isfile(self.path_cfg_web):
                with open(self.path_cfg_web) as json_file:
                    self.cfg_fromjson = jsonload(json_file)
                    return self.cfg_fromjson['event']
            else:
                print('Could not find conf_web.json (from get event function)')
        else:
            return self.cfg_fromjson['event']


    def update_remote(self, alldirs=False):
        def nonrecursive(path):
            # return [os.path.join(path, f) for f in os.listdir(path) if (os.path.isfile(f) and f.endswith('.jpg'))]
            return [f for f in os.listdir(path) if (os.path.isfile(os.path.join(up_local, f)) and f.endswith('.jpg'))]

        if alldirs:
            up_local = self.path_im_local_root
            up_dist = os.path.join(self.ftp.ftpcred["path_web"], 'im')
            local_list = []
            folders = [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(f)]
            for folder in folders:
                local_list.append(nonrecursive(folder))
            #to finish
        else:
            event = self.get_event_folder()
            up_local = os.path.join(self.path_im_local_root, event)
            if os.path.isdir(up_local):
                up_dist = os.path.join(self.ftp.ftpcred["path_web"], 'im', event)
                local_list = nonrecursive(up_local)
                dist_list = self.ftp.ftp_listdir(up_dist)
                to_up = [f for f in local_list if not f in dist_list]

                for f in to_up:
                    self.ftp.ftp_upload(os.path.join(up_local, f), os.path.join(up_dist, f))
            else:
                print(f'Did not find local dir {up_local}, skipping sync')
        # local = [os.path.join(up_local, f) for f in os.listdir(up_local) if (os.path.isfile(f) and f.endswith('.jpg') and not '/raw/' in f)]

    def auto_sync(self):
        print(f'Listening and waiting for new pictures')
        tnow = time.time()
        while True:
            if (time.time() -tnow )>2:
                self.update_remote()
                tnow = time.time()

    def check_internet(self):
        try:
            request.urlopen(self.path_cfg_web_dist, timout=1)
            return True
        except:
            return False


if __name__=='__main__':
    iobj = iobj()
    iobj.auto_sync()

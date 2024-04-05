import os
import urllib.request
import shutil
from json import load as jsonload
from time import sleep as sleep
from base64 import b64decode as dec
from urllib import request
import ftp

class iobj():

    def __init__(self, ftp_on=True):

        self.path_cfg_local = os.path.join(os.path.expanduser('~'), '.config/pibooth/pibooth.cfg')
        self.cfg_fromjson = None

        if os.path.isdir('/USB/im'):
            self.path_im_local_root = '/USB/im/'
        else:
            self.path_im_local_root = os.path.join(os.path.expanduser('~'), 'Pictures/pibooth/')

        if ftp_on:
            self.ftp = ftp.ftp()
            self.ftp.ftp_connection()


    def fetch_cfg_from_web(self):
        try:
            self.ftp.ftp_download(os.path.join(self.ftp.ftpcred["path_web_pibooth"], 'admin/conf_web.json'), 'conf_web.json')
            print('Fichier de configuration téléchargé depuis le web')
        except:
            print('Echec de téléchargement du fichier de configuration')

    def update_cfg_from_json(self):
        self.fetch_cfg_from_web()
        print('Updating config from json file')
        #open local file
        if os.path.isfile('conf_web.json'):
            with open('conf_web.json') as json_file:
                self.cfg_fromjson = jsonload(json_file)

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
            print('Could not find conf_web.json')

    def get_event_folder(self):
        if self.cfg_fromjson is None:
            if os.path.isfile('conf_web.json'):
                with open('conf_web.json') as json_file:
                    self.cfg_fromjson = jsonload(json_file)
            else:
                print('Could not find conf_web.json')
        return self.cfg_fromjson['event']



    # def move_file(self, files, move_dist=True):
    #
    #     if not os.path.isdir(self.path_pic_local_dir):
    #         os.mkdir(self.path_pic_local_dir)
    #     for file in files:
    #         #need to rename
    #         path = os.path.join(self.path_pic_tmp, file)
    #         dest = os.path.join(self.path_pic_local_dir, file)
    #         print(f'Moving {path} to {dest}')
    #         shutil.move(path, dest)
    #         #also move the raw file
    #
    #         #send to server
    #         if move_dist and self.connection is not None:
    #             dist_dir = os.path.join(self.path_pic_dist_root, self.pic_local_dirname)
    #             dist = os.path.join(dist_dir, file)
    #             self.ftp_upload(dest, dist)

    def update_remote(self, alldirs=False):
        def nonrecursive(path):
            # return [os.path.join(path, f) for f in os.listdir(path) if (os.path.isfile(f) and f.endswith('.jpg'))]
            return [f for f in os.listdir(path) if (os.path.isfile(f) and f.endswith('.jpg'))]

        if alldirs:
            up_local = self.path_im_local_root
            up_dist = os.path.join(ftp.ftpcred["path_web_pibooth"], 'im')
            local_list = []
            folders = [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(f)]
            for folder in folders:
                local_list.append(nonrecursive(folder))
            #to finish
        else:
            event = get_event_folder()
            up_local = os.path.join(self.path_im_local_root, event)
            up_dist = os.path.join(self.ftp.ftpcred["path_web_pibooth"], 'im', event)
            local_list = nonrecursive(up_local)
            dist_list = self.ftp.ftp_listdir(up_dist)
            to_up = [f for f in local_list if f not in dist_list]

            for f in to_up:
                self.ftp.upload(os.path.join(up_local, f), os.path.join(up_dist, f))

        # local = [os.path.join(up_local, f) for f in os.listdir(up_local) if (os.path.isfile(f) and f.endswith('.jpg') and not '/raw/' in f)]

    def auto_sync(self):
        print(f'Listening and waiting for new pictures')
        while True:
            update_remote()
            sleep(1)

    def check_internet(self):
        try:
            request.urlopen(self.path_cfg_web_dist, timout=1)
            return True
        except:
            return False


if __name__=='__main__':
    wp = pibooth_wrapper()
    input(wp.check_internet())
    wp.ftp_connection()
    wp.ftp_download(wp.path_cfg_web_dist, wp.path_cfg_web_local)
    wp.update_cfg_from_json()
    wp.auto_sync()
    wp.ftp_disconnect()

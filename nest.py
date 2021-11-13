 # coding=utf-8

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from os import path, remove


class apiConnect():
    def __init__(self):
        super().__init__()
        self.sdm = None
        #self.connect()

    def connect(self):#, setup=False):
        # define path variables
        credentials_file_path = '/home/pi/tempMonitor/credentials/credentials.json'  #pénible.

        # define store
        store = file.Storage(credentials_file_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            return "Not found" #None
        else:
            http = credentials.authorize(Http())
            self.sdm = discovery.build('smartdevicemanagement', 'v1', http=http)
            return self.sdm

    def config(self):
        credentials_file_path = './credentials/credentials.json'
        clientsecret_file_path = './credentials/client_secret_nest.json'

        # define scope
        SCOPE = 'https://www.googleapis.com/auth/sdm.service'

        if path.isfile('./credentials/credentials.json'):
            remove('./credentials/credentials.json')   #if the file exist, might be corrupted and not working, or someone just wants to switch accounts. Delete it.

        # define store
        store = file.Storage(credentials_file_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(clientsecret_file_path, SCOPE)
            credentials = tools.run_flow(flow, store)
        # define API service
        http = credentials.authorize(Http())
        self.sdm = discovery.build('smartdevicemanagement', 'v1', http=http, cache_discovery=False) #cache_discovery=false removes a warning about not finding the cache. Yes.

        return self.sdm

#sdm = apiConnect().connect()




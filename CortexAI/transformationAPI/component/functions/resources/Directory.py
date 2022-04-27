import os

from transformationAPI.component.functions.resources import Adls
import json
from dhub.reference_data.constant import constants 

# takes file structure and create all files within ADLS instance
class Directory(Adls):



 def __init__(self,root_dir):    
     self.root_dir=root_dir
     

    


 # json_object:  file structure as json
 # target_key:    path is the key for file path e.g."path":"C:/file?xxx"
 # self.root_dir  root directory defined by REST API arg['root_dir']
 # constants.file_system containes file system from either hub or spoke

 def create_directory_json_recursively(self,json_object, target_key='path'):
    
    hub=Adls()
    hub.initialize_storage_account(constants.storage_account_name,constants.storage_account_key)
    

    if type(json_object) is dict and json_object:
        
        for key in json_object:
            if key == target_key:
                
                #print("{}: {}".format(target_key, json_object[key]))
                hub.create_directory(constants.file_system,path=constants.file_system+'/'+json_object[key])
                #print(json_object[key])
            self.create_directory_json_recursively(json_object[key], target_key)

    elif type(json_object) is list and json_object:
        for item in json_object:
            self.create_directory_json_recursively(item, target_key)



'''

if __name__ == '__main__':
    hub=Directory('jzou')
    hub.initialize_storage_account(constants.storage_account_name,constants.storage_account_key)

    with open(r'dhub\reference_data\constant\data.json') as f:
        data = json.load(f)

        hub.create_directory_json_recursively(data)

'''
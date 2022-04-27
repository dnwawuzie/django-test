
import os, uuid, sys
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core._match_conditions import MatchConditions
from azure.storage.filedatalake._models import ContentSettings
from azure.identity import ClientSecretCredential
from dhub.reference_data.constant import constants

#a class that contains methods needed for ADLS , needs to be implemented 

class Adls:

 
 
 def __init__(self):
     '''
     self.AZURE_TENANT_ID = AZURE_TENANT_ID
     self.AZURE_CLIENT_ID = AZURE_CLIENT_ID
     self.AZURE_CLIENT_SECRET = AZURE_CLIENT_SECRET
     self.AZURE_SUBSCRIPTION_ID = AZURE_SUBSCRIPTION_ID
     '''
			
 def initialize_storage_account(self,storage_account_name, storage_account_key):
    
    try:  
        global service_client

        service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
            "https", storage_account_name), credential=storage_account_key)
    
    except Exception as e:
        print(e)
    

 #Connect by using Azure Active Directory (AD)

 def initialize_storage_account_ad(self,storage_account_name, client_id, client_secret, tenant_id):
   
    try:  
     global service_client

     credential = ClientSecretCredential(tenant_id, client_id, client_secret)

     service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
          "https", storage_account_name), credential=credential)
   
    except Exception as e:
     print(e)


 #Create a container
 def create_file_system(self,file_system):
      
     try:
      global file_system_client

      file_system_client = service_client.create_file_system(file_system)
      print('file system has been created')
     except Exception as e:
      print(e)



 #Create a directory
 def create_directory(self,file_system,path):
     try:
         file_system_client = service_client.get_file_system_client(file_system)
         file_system_client.create_directory(path)
         print ('directory',path, 'has been created')
   
     except Exception as e:
      print(e)


 #Rename or move a directory
 def rename_directory(self,file_system,path,new_dir_name):
    try:
       
       file_system_client = service_client.get_file_system_client(file_system)
       directory_client = file_system_client.get_directory_client(path)
       
       new_dir_name = new_dir_name
       directory_client.rename_directory(rename_destination=directory_client.file_system_name + '/' + new_dir_name)

    except Exception as e:
     print(e)


  #Delete a directory
 def delete_directory(self,file_system,path):
    try:
        file_system_client = service_client.get_file_system_client(file_system)
        directory_client = file_system_client.get_directory_client(path)

        directory_client.delete_directory()
        print('directory',path,'has been deleted')
    except Exception as e:
     print(e)



 #Upload a file to a directory
 def upload_file_to_directory(self,file_system,path):
    try:

     file_system_client = service_client.get_file_system_client(file_system)

     directory_client = file_system_client.get_directory_client(path)
     
     file_client = directory_client.create_file("uploaded-file.txt")
     local_file = open(r"C:\Users\juzou\Desktop\test.txt")

     file_contents = local_file.read()

     file_client.append_data(data=file_contents, offset=0, length=len(file_contents))

     file_client.flush_data(len(file_contents))

    except Exception as e:
     print(e)


 #List directory contents
 def list_directory_contents(self,file_system,path):
    try:
     
     file_system_client = service_client.get_file_system_client(file_system)

     paths = file_system_client.get_paths(path)

     
     dict = {}
     dict[file_system] = []

     for path in paths:
          dict[file_system].append(path.name)
          

     return dict

 

     

    except Exception as e:
     print(e)




 # list all files within hub, and move each file  to spoke

 # hub_file_system : the file system in hub ADLS
 # spoke_file_system : the file system in spoke ADLS that we want to move to
 # path : root directory within hub file system
 def move_directory_from_hub_to_spoke(self,hub_file_system,path,spoke_file_system):

    spoke=Adls()
    spoke.initialize_storage_account(constants.storage_account_name,constants.storage_account_key)

    try:
     
     file_system_client = service_client.get_file_system_client(hub_file_system)

     paths = file_system_client.get_paths(path)

     for path in paths:
      spoke.create_directory(spoke_file_system,path.name)
      print(path.name , 'has been moved to spoke')
    except Exception as e:
     print(e)

 #Upload a file to a directory
 def move_file_from_hub_to_spoke(self,hub_file_system,hub_path,spoke_file_system,spoke_path):
    try:
     hub_service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
            "https", constants.storage_account_name), credential=constants.storage_account_key)
     spoke_service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
            "https", constants.storage_account_name), credential=constants.storage_account_key)


     hub_file_system_client = hub_service_client.get_file_system_client(file_system)
     spoke_file_system_client = spoke_service_client.get_file_system_client(file_system)


     hub_directory_client = hub_file_system_client.get_directory_client(hub_path)
     spoke_directory_client = spoke_file_system_client.get_directory_client(spoke_path)
     
     
     
     

     paths = hub_file_system_client.get_paths(hub_path)

     for path in paths:
      spoke_file_client = spoke_directory_client.create_file(path.name)
      hub_file_client = hub_directory_client.get_file_client(path.name)

      
      hub_data=hub_file_client.read()
      #could be useful
      #download = hub_file_client.download_file()
      #downloaded_bytes = download.readall()
      #local_file.write(downloaded_bytes)
      #local_file.close()
      spoke_file_client=upload_data(hub_data, overwrite=True)

    except Exception as e:
     print(e)




 #Manage directory ACLs
 def manage_directory_permissions(self,file_system,path):
    try:
     file_system_client = service_client.get_file_system_client(file_system)

     directory_client = file_system_client.get_directory_client(path)
     
     acl_props = directory_client.get_access_control()
     
     print(acl_props['permissions'])
     
     new_dir_permissions = "rwxr-xrw-"
     
     directory_client.set_access_control(permissions=new_dir_permissions)
     
     acl_props = directory_client.get_access_control()
     
     print(acl_props['permissions'])
   
    except Exception as e:
     print(e)



  #Manage file permissions
 def manage_file_permissions(self,file_system,path):
    try:
        file_system_client = service_client.get_file_system_client(file_system)

        directory_client = file_system_client.get_directory_client(path)
        
        file_client = directory_client.get_file_client("uploaded-file.txt")

        acl_props = file_client.get_access_control()
        
        print(acl_props['permissions'])
        
        new_file_permissions = "rwxr-xrw-"
        
        file_client.set_access_control(permissions=new_file_permissions)
        
        acl_props = file_client.get_access_control()
        
        print(acl_props['permissions'])

    except Exception as e:
     print(e)


    '''
    def run():
    #print(__name__)
    adls=Adls('')
    adls.initialize_storage_account()

    if __name__ == '__main__':
    run()

    '''